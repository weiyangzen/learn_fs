# Research: sources/distributed-fs/ceph-client/rust/kernel/time/hrtimer/tbox.rs

## sources/distributed-fs/ceph-client/rust/kernel/time/hrtimer/tbox.rs

Purpose: implements hrtimer support for heap-owned pinned boxes. Important APIs are `BoxHrTimerHandle<T, A>`, `HrTimerHandle::cancel`, `Drop`, `HrTimerPointer for Pin<Box<T, A>>`, and `RawHrTimerCallback for Pin<Box<T, A>>`.

Control flow: starting consumes `Pin<Box<T, A>>`, unsafely removes the pin wrapper without moving `T`, converts the box into a raw pointer, starts the embedded timer, and stores the pointer in the handle. Drop cancels then reconstructs and drops the box. Callback dispatch finds the enclosing `T`, creates `Pin<&mut T>`, builds context, and calls `T::run`. State is raw box ownership in `NonNull<T>` plus allocator marker. Dependencies include `Box`, `Pin`, allocator trait, `HasHrTimer`, and hrtimer callback traits. Integration points are one-shot or repeating timer objects whose lifetime should be owned by the timer handle. Risks include raw ownership bugs if invariants are changed, leaks preserving the allocation/timer indefinitely, mutable callback access requiring no competing aliases, and unsafe `Pin::into_inner_unchecked` correctness. Test signals: handle drop frees allocation after cancellation, callback mutation through `Pin<&mut T>`, restart/no-restart behavior, and allocator-generic builds.
