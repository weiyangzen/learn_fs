# sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_linux.go

Purpose: utility functions for CPU mask conversion, irqbalance config editing, service control, and file checks used by Linux runtime hooks.

Important APIs/types/functions: `isASCII`, `cpuMaskByte`, `mapHexCharToByte`, `mapByteToHexChar`, `invertByteArray`, `isAllBitSet`, `calcIRQSMPAffinityMask`, `restartService`, `isServiceEnabled`, `updateIrqBalanceConfigFile`, `retrieveIrqBannedCPUMasks`, and `fileExists`.

Control flow: mask helpers parse comma-separated hex masks into little-endian byte arrays, set or clear CPU bits, compute inverted banned masks, pad to kernel-friendly 32-bit boundaries, and return comma-grouped hex strings. Config helpers replace or append `IRQBALANCE_BANNED_CPUS` lines.

State and persistence behavior: reads/writes irqbalance config files and executes `systemctl`. Mask helpers are pure.

Dependencies and integration points: depends on `hex`, `os`, `strings`, logrus, Kubernetes cpuset, and CRI-O command runner.

Risks: `calcIRQSMPAffinityMask` assumes the current mask is long enough for every CPU index. Config parsing uses a simple split on `=`, so unusual shell syntax is not preserved. `systemctl` calls depend on host service manager.

Test signals: utility tests cover bit set/clear cases, odd-length masks, short masks, inverse mask generation, and bounded config-file line count.
