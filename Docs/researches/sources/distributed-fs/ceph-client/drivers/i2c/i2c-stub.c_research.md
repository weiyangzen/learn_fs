# sources/distributed-fs/ceph-client/drivers/i2c/i2c-stub.c

Purpose: software SMBus adapter and chip emulator for testing I2C client drivers without hardware. It creates one virtual adapter and emulates up to ten configured chip addresses with byte, word, I2C-block, and optional SMBus-block register behavior.

Important APIs/types: module parameters include `chip_addr`, `functionality`, `bank_reg`, `bank_mask`, `bank_start`, and `bank_end`. `struct stub_chip` stores the current pointer, 256 word registers, SMBus block list, and optional banked-register storage. The adapter algorithm exposes `stub_xfer()` and `stub_func()`.

Control flow: init validates chip addresses, allocates chip state, initializes SMBus block lists and optional banks, then registers `stub_adapter`. Transfers find the emulated chip by address and implement SMBus command semantics: byte writes update pointer, byte/word data access register storage, I2C block accesses sequential byte registers, and SMBus block writes create/update per-command block buffers. Bank selection changes when the configured bank register is written.

State and persistence: all emulated register and block data live in module memory and reset on module unload. `functionality` is writable and can change advertised capabilities at runtime.

Dependencies and integration: depends on the I2C core adapter registration and SMBus algorithm path. It is typically used with client-driver tests or manual `i2c-dev` transactions.

Risks: no locking protects chip register state, so concurrent users can race. Bank masks assume contiguous bits. SMBus block reads require a prior block write. It does not emulate timing, interrupts, PEC, or real hardware side effects.

Test signals: module load with valid/invalid addresses, client probing on the virtual adapter, byte/word/block command behavior, banked register selection, runtime functionality masking, and cleanup on unload.
