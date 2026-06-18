<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Kbuild -->
# sources/distributed-fs/ceph-client/Kbuild

## Purpose
Top-level Kbuild file for the Linux kernel tree. It performs global preparation steps, validates generated headers, checks syscall coverage, and declares the ordinary directory descent order for the full kernel build.

## Important APIs, Types, And Functions
- Generated headers: `include/generated/bounds.h`, `timeconst.h`, `asm-offsets.h`, and `rq-offsets.h`.
- Targets include `prepare`, `missing-syscalls`, generated assembly prerequisites, and atomic header checks.
- Uses Kbuild macros `filechk`, `if_changed`, and `if_changed_dep`.
- `obj-y` and conditional `obj-$(CONFIG_*)` entries enumerate top-level build directories.

## Control Flow
Preparation first builds assembly intermediates for bounds and offsets, then converts them into generated headers. `timeconst.h` is generated through `bc` using `CONFIG_HZ`. `missing-syscalls` runs `scripts/checksyscalls.sh` after scheduler runqueue offsets exist. Atomic headers are checked by comparing a trailing embedded SHA1 with the hash of the file body. The final section declares recursive descent into init, arch, kernel, mm, fs, drivers, net, and other top-level directories.

## State And Persistence
Writes generated headers under `include/generated/`, temporary `.tmp_missing-syscalls*` files, and `.checked-*` stamp targets for atomic header validation. These are build artifacts cleaned by the kernel build system.

## Dependencies And Integration Points
Depends on compiler-generated assembly, `bc`, `sha1sum`, Kbuild include macros, scheduler and arch offset sources, and top-level directory Makefiles. It is invoked by the root `Makefile` during `prepare` and normal recursive build descent.

## Risks And Edge Cases
Preparation ordering is critical because many later objects include generated headers. Missing `bc` or mismatched atomic header hashes fail early. The syscall check depends on arch syscall metadata and can expose incomplete architecture wiring.

## Test Signals
`make prepare`, `make missing-syscalls`, and a normal kernel build are primary signals. Touching bounds/offset source files should regenerate matching headers; manual edits to generated atomic headers should fail the SHA1 check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Kbuild -->
