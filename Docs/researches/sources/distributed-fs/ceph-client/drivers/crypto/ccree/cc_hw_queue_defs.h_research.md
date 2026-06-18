# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hw_queue_defs.h

## Purpose

`cc_hw_queue_defs.h` defines the six-word CryptoCell hardware descriptor format, enumerations for DMA/flow/setup/cipher fields, and inline setters that pack descriptor words. It is the main abstraction used by cipher, AEAD, hash, SRAM, and request manager code to build hardware command sequences.

## Important APIs, Types, And Functions

`struct cc_hw_desc` stores six 32-bit descriptor words. Macros derive bit masks from `cc_kernel_regs.h` field definitions. Enumerations describe AXI security, descriptor direction, DMA modes (`NO_DMA`, `DMA_SRAM`, `DMA_DLLI`, `DMA_MLLI`), flow modes, setup operations, hash padding/configuration, AES MAC selectors, hardware key slots, AES key sizes, and hash padding commands.

Setter functions include `hw_desc_init()`, `set_queue_last_ind_bit()`, `set_din_type()`, `set_din_no_dma()`, `set_cpp_crypto_key()`, `set_din_sram()`, `set_din_const()`, `set_din_not_last_indication()`, `set_dout_type()`, `set_dout_dlli()`, `set_dout_mlli()`, `set_dout_no_dma()`, `set_xor_val()`, `set_xor_active()`, `set_aes_not_hash_mode()`, `set_aes_xor_crypto_key()`, `set_dout_sram()`, `set_xex_data_unit_size()`, `set_multi2_num_rounds()`, `set_flow_mode()`, `set_cipher_mode()`, `set_hash_cipher_mode()`, `set_cipher_config0()`, `set_cipher_config1()`, `set_hw_crypto_key()`, `set_bytes_swap()`, `set_cmac_size0_mode()`, `set_key_size()`, `set_key_size_aes()`, `set_key_size_des()`, `set_setup_mode()`, and `set_cipher_do()`.

## Control Flow

The header has no runtime loop, but it controls descriptor construction order in callers. Callers initialize a descriptor, set DIN/DOUT fields, select flow and cipher mode, add setup operation and key/padding flags, then submit the sequence through the request manager. For 64-bit DMA builds, high address halves are packed into word 5.

## State And Persistence Behavior

Descriptors are transient command records. Once written to `DSCRPTR_QUEUE_WORD0`, hardware consumes the six words and updates engine state, SRAM, or DMA buffers depending on flow mode. The setters mutate only in-memory descriptor arrays.

## Dependencies And Integration Points

The header includes `cc_kernel_regs.h` for bitfield offsets and Linux `bitfield.h` for `FIELD_PREP`. It is used across the ccree driver wherever hardware work is described. `set_hash_cipher_mode()` contains an SM3-specific integration detail: it sets `AES_XOR_CRYPTO_KEY` to select the SM3 engine path for that hash mode.

## Risks And Edge Cases

These setters mostly OR fields into words; callers must start from `hw_desc_init()` or stale fields can survive. Field sizes limit DIN/DOUT sizes to descriptor bit widths, while MLLI entries have a smaller 16-bit per-entry limit. `set_key_size_aes()` expects byte sizes and converts to hardware codes; passing a code instead of bytes would program the wrong key length. Queue-last and DOUT-last are distinct bits and confusing them can hang flows or suppress completions.

## Test Signals

Descriptor dumps under `cc_dump_desc`, crypto self-tests for each flow mode, 64-bit DMA address testing, hardware-key/CPP paths, SM3 tests, and MLLI scatterlist tests provide useful validation that bit packing matches hardware.
