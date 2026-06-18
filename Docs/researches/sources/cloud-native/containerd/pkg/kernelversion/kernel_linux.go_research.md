# sources/cloud-native/containerd/pkg/kernelversion/kernel_linux.go

Purpose: Linux kernel version parser and comparator used by features that need minimum kernel gates.

Important APIs/types/functions: `KernelVersion` stores `Kernel` and `Major` integers and formats as `kernel.major`. Package variable `kernelVersion` caches detected host version. `getKernelVersion` calls `unix.Uname`, converts `Utsname.Release` through `unix.ByteSliceToString`, parses it, and caches the result. `parseRelease` scans two dot-separated integers using `fmt.Fscanf`. `GreaterEqualThan(minVersion)` compares current kernel major/minor against a minimum.

Control flow: first comparison loads and caches the host kernel. Parsing accepts release strings with extra suffix after the second number because scanning stops after the major component.

State/persistence: process-global in-memory cache only. No disk persistence.

Dependencies/integration: depends on `golang.org/x/sys/unix`. Copied/customized from Moby seccomp kernel version handling.

Risks: cache never refreshes during process lifetime. Parser ignores patch level and distribution suffix semantics. The name `Major` represents the second component, which can be confused with semantic-version major naming.

Test signals: `kernel_linux_test.go` covers host detection, accepted release formats, parse errors, and comparison outcomes.
