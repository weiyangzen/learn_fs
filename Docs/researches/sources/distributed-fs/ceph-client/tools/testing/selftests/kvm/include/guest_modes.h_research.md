# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/guest_modes.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/guest_modes.h

Purpose: common registry for guest address-size/page-size modes supported by KVM selftests. It lets tests append defaults, iterate selected modes, print help, and parse mode-related command-line arguments.

Important APIs/types/functions: `struct guest_mode { bool enabled; bool supported; }`, global `guest_modes[NUM_VM_MODES]`, `guest_mode_append(mode, enabled)`, `guest_modes_append_default`, `for_each_guest_mode`, `guest_modes_help`, and `guest_modes_cmdline`.

Control flow and state: process-global `guest_modes` stores which `enum vm_guest_mode` values are available and enabled. Tests populate defaults, allow CLI overrides, then call `for_each_guest_mode()` to run mode-parametrized test bodies.

Dependencies and integration: depends on `kvm_util.h` for `enum vm_guest_mode` and mode parameters. It integrates with architecture-specific mode defaults and tests that need coverage across page sizes or address widths.

Risks: mode state is global and mutable, so tests must initialize it predictably before iteration. Unsupported modes need to be filtered or skipped to avoid false failures on host-specific limitations.

Test signals: command-line selftest runs with guest-mode options, plus multi-mode memory-management tests, validate parsing and iteration behavior.
