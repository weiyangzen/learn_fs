# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/tprot.c

## Purpose
This s390x test verifies KVM emulation and interpretation behavior for the TEST PROTECTION (`tprot`) instruction under storage-key, fetch-protection, translation-unavailable, and CR0 override conditions.

## Important APIs, Types, And Functions
Guest helpers use `sske`, `lra`, and `tprot`. The test manipulates host memory permissions with `mprotect()` to force DAT protection and writes CR0 override bits through `run->s.regs.crs[0]` with `KVM_SYNC_CRS`. The `tests[]` table defines stages, target addresses, access keys, and expected permission results.

## Control Flow
Guest code sets storage keys for two test pages, syncs to host, executes the simple table stage, tries to set key on page zero for fetch-override tests, and then runs fetch and storage override stages. The host creates the VM, write-protects test pages, optionally maps guest page zero, sets fetch-protection override, then storage-protection override, and synchronizes at each stage. Skips are handled when page zero cannot be allocated at address 0.

## State, Dependencies, And Integration
State spans guest storage keys, host page permissions, optional guest page-zero mapping, and CR0 override bits. It depends on shared host/guest page tables, s390 storage-key instructions, and KVM's emulation of `tprot` when DAT protection causes interception.

## Risks And Test Signals
Risks include incorrect permission code translation, failure to respect 0-2048 fetch-protection override limits, and page-zero allocation variability. Signals are planned stage PASS/SKIP lines and guest assertions comparing every `tprot` result to the table.
