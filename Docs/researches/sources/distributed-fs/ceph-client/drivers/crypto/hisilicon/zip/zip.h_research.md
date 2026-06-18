# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip.h

## Purpose
This header is the shared contract between HiSilicon ZIP device management, Crypto API compression, and DAE support. It defines common driver structures, the ZIP SQE layout, capability table indexes, and cross-file function prototypes.

## Important APIs, Types, And Functions
`struct hisi_zip` embeds `struct hisi_qm`, a PF-only control pointer, and ZIP DFX counters. `struct hisi_zip_dfx` provides `send_cnt`, `recv_cnt`, `send_busy_cnt`, and `err_bd_cnt`. `struct hisi_zip_sqe` maps the 128-byte hardware SQE used by `zip_crypto.c`, including consumed/produced lengths, status, request type, buffer type, source/destination addresses, and tag fields. `enum zip_cap_table_type` indexes stored capability records.

Declared functions connect the module pieces: queue allocation (`zip_create_qps()`), Crypto API registration (`hisi_zip_register_to_crypto()`, `hisi_zip_unregister_from_crypto()`), algorithm capability checking (`hisi_zip_alg_support()`), and DAE helpers.

## Control Flow
The header has no execution, but its declarations define the module graph: `zip_main.c` owns PCI/QM lifecycle and calls into `zip_crypto.c` and `dae_main.c`; `zip_crypto.c` uses `struct hisi_zip_sqe` to submit compression requests; DAE callbacks are invoked from ZIP error and initialization paths.

## State And Persistence
No state is allocated in the header. The structs describe in-memory per-device state and transient hardware SQEs. The DFX counters are atomic runtime state exposed by debugfs.

## Dependencies And Integration Points
It depends on `linux/hisi_acc_qm.h` for QM types and error-result enums. The header is private to the HiSilicon ZIP directory and coordinates all three object files in the composite module.

## Risks
The SQE layout is hardware ABI. Field order and comments must stay aligned with descriptor fill/parsing in `zip_crypto.c`. Capability enum order must match capability table initialization in `zip_main.c`; any drift would cause wrong algorithm registration or debug reporting.

## Test Signals
Build tests catch prototype drift. Runtime tests should verify SQE submission/completion for deflate/lz4, DFX counter exposure, and algorithm filtering from capability table indexes.
