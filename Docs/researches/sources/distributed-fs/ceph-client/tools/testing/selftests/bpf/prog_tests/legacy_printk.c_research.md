
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/legacy_printk.c

## Purpose

`legacy_printk.c` verifies both legacy and modern `bpf_printk`-style paths, while allowing the modern variant to fail loading on older kernels.

## Important APIs, Types, and Functions

It uses `test_legacy_printk.skel.h`, toggles autoload for `handle_legacy` or `handle_modern`, updates/reads maps for the legacy path, uses BSS variables for the modern path, attaches the skeleton, and sleeps briefly to trigger.

## Control Flow and Data Flow

`test_legacy_printk()` requires `execute_one_variant(true)` to succeed. The legacy variant writes current PID into `my_pid_map`, attaches, then reads `res_map`. The modern variant sets `bss->my_pid_var`, attaches if load succeeded, and reads `bss->res_var`; its return is not asserted by the top-level test.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is map-stored PID/result for legacy mode and BSS PID/result for modern mode. Dependencies include trace attachment support and kernel support for modern printk globals if that variant is to pass. Integration is compatibility between legacy map-based and modern global-variable-based printk use. Risks are load failure accepted for modern path and trigger timing via `usleep(1)`. Test signal is legacy result greater than zero; modern result greater than zero when load succeeds.
