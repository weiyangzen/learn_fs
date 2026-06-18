# File Research: sources/cow-pools/bcachefs-tools/fs/util/darray.h

Macro-based dynamic-array library. It defines preallocated and heap-only array shapes, init/exit helpers, cleanup classes, typed aliases, push/pop/resize/make-room helpers, iteration macros, insert/remove/find helpers, and sort/search wrappers.

RCU resize variants preserve readers, and free-item variants run per-element destructors. Eytzinger sort/find wrappers support one-based arrays with a reserved element at index 0.
