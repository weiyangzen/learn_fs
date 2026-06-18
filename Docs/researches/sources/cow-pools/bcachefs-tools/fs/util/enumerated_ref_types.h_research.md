# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref_types.h

Defines `struct enumerated_ref`. Debug builds store user count, dying flag, and atomic array; normal builds store a `percpu_ref`. Both variants include an optional stop callback and completion used by stop/wait paths.
