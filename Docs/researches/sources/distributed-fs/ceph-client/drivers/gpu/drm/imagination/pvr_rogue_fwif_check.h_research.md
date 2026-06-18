# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_check.h

Purpose: This companion header is the compile-time ABI verifier for `pvr_rogue_fwif.h`. It asserts exact offsets and sizes for FW-shared structures so the host compiler cannot silently produce layouts that differ from firmware expectations.

Important APIs/types/functions: The exported macros are `OFFSET_CHECK(type, member, offset)` and `SIZE_CHECK(type, size)`, both backed by `static_assert`. The checks cover trace buffers, fault records, `rogue_fwif_sysdata`, SLR/OS data, HWR info, memory/context objects, KCCB/FWCCB payloads, runtime configuration, connection and compatibility checks, OS init, signature/counter dump controls, PDVFS OPPs, HWPerf BVNC, system init, GPU utilization control block, RTA control, freelists, HWRT common/data, and sync checkpoint records.

Control flow: None at runtime. Inclusion from `pvr_rogue_fwif.h` causes C compilation to fail if any checked structure layout diverges.

State and persistence behavior: No storage is introduced. The file protects persisted shared-memory layouts by forcing exact binary positions for fields such as queue offsets, fault logs, context addresses, timer correlation state, and freelist/HWRT metadata.

Dependencies and integration points: It depends on `offsetof` availability through included compiler headers and includes `linux/build_bug.h`. It must be included after the relevant structs are declared. It is an integration gate between kernel C ABI, firmware ABI, and generated layout expectations.

Risks: Missing checks allow ABI drift; stale checks block intentional ABI updates until firmware and host are changed together. The assertions also assume compiler enum size and alignment behavior, so toolchain option changes can surface here. Because it checks many large structs, failures should be treated as compatibility issues rather than style problems.

Test signals: Any kernel build including `pvr_rogue_fwif.h` exercises this header. Useful review signals are deliberate offset-change compile failures, CI builds across supported architectures/compilers, and firmware compatibility tests after any FWIF structure edit.
