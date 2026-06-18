# sources/control-plane/mayastor/io-engine/tests/core.rs

Purpose: core bdev/nexus integration tests covering basic nexus creation/destruction, descriptor/channel use, exclusive opens, size validation, shared device size, and failure when a child path is inaccessible.

Important APIs/types/functions: `do_uring` detects kernel io_uring support. `create_nexus` chooses AIO and optionally uring children. Tests use `nexus_create`, `nexus_lookup_mut`, `UntypedBdev::open_by_name`, `UntypedBdevHandle::open`, `bdev_create`, `bdev_destroy`, and `share(Protocol::Off)`.

Control flow: `core` prepares temp files and calls `works`. `works` creates/destroys a nexus and opens an I/O channel. `core_2` opens two write descriptors and channels, then drops them before destroy. `core_3` verifies exclusive handle open rejects a second exclusive opener. `core_4` iterates child-size/add-child size cases. `core_5` shares a single-child nexus with `Protocol::Off` and checks visible device size does not exceed requested nexus size. `core_6` creates a URI for a missing file and expects nexus creation failure.

State and persistence: uses `/tmp/disk*.img` temp files. `DO_URING` is cached in a mutable static guarded by `Once`. Mayastor instance is shared via `OnceCell`.

Dependencies and integration points: AIO/uring bdev providers, nexus size checks, bdev descriptor/channel lifecycle, sharing path, and kernel io_uring support.

Risks and edge cases: mutable static is used for uring support. Fixed temp file names and a shared Mayastor instance can interfere with parallel tests. Some tests assume previous file setup from earlier tests unless run order/environment provides the files.

Test signals: good coverage of bdev lifecycle invariants, exclusive open behavior, and child-size enforcement.
