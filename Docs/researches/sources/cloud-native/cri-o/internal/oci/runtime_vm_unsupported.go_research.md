# sources/cloud-native/cri-o/internal/oci/runtime_vm_unsupported.go

## Purpose
Non-Linux fallback for VM runtime stats.

## Behavior and Risks
`CgroupStats` and `DiskStats` both return unsupported errors. This preserves build portability while making VM stats Linux-only. No direct tests cover this path.
