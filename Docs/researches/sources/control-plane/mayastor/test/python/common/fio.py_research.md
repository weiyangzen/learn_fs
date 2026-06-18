# sources/control-plane/mayastor/test/python/common/fio.py

## Purpose
Builds fio command strings for kernel-device IO tests.

## Important APIs, Types, And Functions
Defines class `Fio` with constructor parameters for job name, rw mode, device(s), optional size, runtime, and extra options; `build()` returns a `nix-sudo fio` command using `linuxaio`, direct IO, 4 KiB blocks, iodepth 64, group reporting, and `norandommap`.

## Control Flow
`build` normalizes a single device to a list, joins multiple devices with `:`, conditionally adds `--size`, and formats the command.

## State And Persistence
The object stores command configuration plus unused `output` and `success` dictionaries. fio itself writes to the target devices only when the built command is executed by tests.

## Dependencies And Integration Points
Used throughout nexus, multipath, fault, and Kubernetes-style tests to generate fio workloads. Depends on `shutil.which("fio")` but the built command uses `$PATH` via `nix-sudo fio`.

## Risks
The command is returned as a shell string, so tests that split it can break if option strings contain spaces. Privileged execution and local fio availability are required.

## Test Signals
fio exit code zero and uninterrupted runtime are used as datapath health signals for connected NVMe devices and mounted filesystems.
