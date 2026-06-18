# sources/distributed-fs/ceph-client/tools/hv/vmbus_testing

## Purpose

`vmbus_testing` is a Python 3 command-line tool for enabling, disabling, and viewing Hyper-V VMBus fuzz-test controls exposed through debugfs. Its current test method controls buffer interrupt delay and message delay attributes.

## Important APIs and Flow

The script uses `argparse` subcommands: `delay`, `disable_all`/`D`, `disable_single`/`d`, `view_all`/`V`, and `view_single`/`v`. It expects `/sys/kernel/debug/hyperv` and recursively builds a `file_map` from device directories to debugfs files. Enums `dev_state` and `f_names` define on/off values and known file names: `fuzz_test_state`, `fuzz_test_buffer_interrupt_delay`, and `fuzz_test_message_delay`. Helper functions validate paths and delay ranges, read and write debugfs attributes, locate per-device state files, set delays for one or all devices, and disable tests.

## State, Dependencies, and Integration

The script does not persist its own state; it writes kernel debugfs attributes that affect Hyper-V driver behavior. It depends on debugfs being mounted, Hyper-V debugfs support, file permissions, and the exact file names from `drivers/hv/debugfs.c`. `lsvmbus` is referenced as the way to identify device types before using paths.

## Risks and Test Signals

It exits on invalid inputs and I/O failures, which is appropriate for a test tool but means partial writes can occur during all-device operations. Recursive discovery assumes a stable debugfs directory shape and uses string splitting to print device names. Delay values allow `-1` as keep-previous but reject zero and values above 1000 microseconds. Tests should use a fake debugfs tree for parser and file-map behavior, plus real Hyper-V debugfs tests for delay effects and cleanup through `disable_all`.
