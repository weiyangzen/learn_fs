# sources/cloud-native/cri-o/internal/oci/oci_windows.go

## Purpose
Windows-specific stubs for process kill, exit-code extraction, and TTY command support.

## Behavior, Integration, and Risks
`kill` finds and kills a Windows process. `getExitCode` unwraps `exec.ExitError` and `windows.WaitStatus`. `ttyCmd` returns unsupported. The function names do not fully mirror Unix exports in this subset, indicating Windows support is limited and may only satisfy build needs. No tests cover this path.
