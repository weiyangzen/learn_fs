# sources/cloud-native/cri-o/internal/oci/finished_32.go

## Purpose
Linux arm/386 implementation for deriving finish time from exit-file ctime with explicit integer conversion.

## Behavior, Integration, and Risks
`getFinishedTime` mirrors the main Linux implementation but converts `st.Ctim.Sec` and `st.Ctim.Nsec` to `int64`. It supports `runtime_oci.go` exit-file status handling on 32-bit builds. Risk is limited to stat type assumptions and ctime semantics.
