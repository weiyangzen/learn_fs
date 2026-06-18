# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-ops.c

## Purpose

`ccp-ops.c` is the command execution layer for the AMD Cryptographic Coprocessor. It translates high-level `struct ccp_cmd` requests into CCP hardware operations for AES, AES-CMAC, AES-GCM, XTS-AES, 3DES, SHA/HMAC, RSA, passthrough DMA/bitwise operations, and ECC. It also owns the common scatterlist, DMA scratch-buffer, local storage block, endian conversion, and command completion/error propagation mechanics used by those engines.

## Important APIs, Types, And Functions

The only exported function here is `ccp_run_cmd()`, which dispatches by `cmd->engine`. Core helpers include `ccp_init_sg_workarea()`, `ccp_update_sg_workarea()`, `ccp_init_dm_workarea()`, `ccp_init_data()`, `ccp_prepare_data()`, `ccp_process_data()`, `ccp_copy_to_sb()`, and `ccp_copy_from_sb()`. Operation handlers include `ccp_run_aes_cmd()`, `ccp_run_aes_cmac_cmd()`, `ccp_run_aes_gcm_cmd()`, `ccp_run_xts_aes_cmd()`, `ccp_run_des3_cmd()`, `ccp_run_sha_cmd()`, `ccp_run_rsa_cmd()`, `ccp_run_passthru_cmd()`, `ccp_run_passthru_nomap_cmd()`, and the ECC math helpers. SHA initial constants are stored as big-endian arrays and copied into CCP local storage with hardware byte-swap passthrough.

## Control Flow

Each handler validates command sizes, key lengths, IVs, buffer presence, and version support, then allocates DMA-visible workareas or maps scatterlists. Key and context material is copied into CCP storage-block slots, usually with 256-bit byte swapping to match engine endian requirements. Data is processed in looped chunks chosen from the current source and destination DMA scatterlist entries; short or split entries are staged through a DMA pool buffer. Hardware submission is performed through `cmd_q->ccp->vdata->perform` callbacks. After each chunk, workarea cursors are advanced and final state such as IV, digest, authentication tag, RSA output, or ECC coordinates is copied back to caller buffers.

## State And Persistence Behavior

The file maintains no persistent device state of its own except per-command job IDs generated from `ccp->current_id` on version 3 devices. Most state is transient stack or allocated DMA workarea state. The handlers mutate caller-provided contexts: AES/XTS IVs, SHA contexts or final digests, GCM tags, RSA/ECC result buffers, and `cmd->engine_error`. Local storage block contents persist only for the lifetime of a submitted job and are allocated by the command queue.

## Dependencies And Integration Points

This layer depends on `ccp-dev.h` for queue/device structures and hardware action callbacks, Linux scatterlist/DMA APIs, crypto constants for AES/DES/SHA, and `linux/ccp.h` command layouts. It is reached from the CCP device queueing path and is sensitive to hardware version data such as `rsamax`, storage-block layout, and supported callbacks like `des3`.

## Risks And Test Signals

Risks include DMA mapping lifetime bugs, scatterlist cursor mistakes around DMA-merged entries, incorrect endian conversion or storage-block offsets, in-place detection using only first-entry virtual addresses, command-buffer leaks on error paths, GCM tag validation mistakes, and SNP/KVM-visible crypto regressions from engine-specific validation changes. Test signals include crypto selftests for AES modes, CMAC, GCM auth failure, SHA/HMAC including zero-length input, RSA sizes up to hardware maximum, passthrough alignment cases, ECC success/error bits, DMA API debug, IOMMU enabled boots, and hardware command error propagation through `cmd->engine_error`.
