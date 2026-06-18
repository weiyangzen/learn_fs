# sources/distributed-fs/ceph-client/rust/kernel/alloc/kbox.rs

## Purpose
Implements the kernel's allocator-parameterized Rust `Box` type, including kmalloc/vmalloc/kvmalloc aliases, fallible construction, pinning, in-place initialization, foreign ownership transfer, and vmalloc page iteration.

## APIs, Types, and Functions
`Box<T, A>` is a transparent wrapper around `NonNull<T>` plus allocator marker. Aliases are `KBox`, `VBox`, and `KVBox`. Core APIs include unsafe `from_raw()`, `into_raw()`, `leak()`, `new()`, `new_uninit()`, `pin()`, `pin_slice()`, `into_pin()`, `drop_contents()`, and `into_inner()`. `Box<MaybeUninit<T>, A>` supports `assume_init()` and `write()`. Trait impls cover `ZeroableOption`, `Send`, `Sync`, `From<Box> for Pin<Box>`, `InPlaceWrite`, `InPlaceInit`, `ForeignOwnable` for boxed and pinned values, `Deref`, `DerefMut`, `Borrow`, `BorrowMut`, `Display`, `Debug`, `Drop`, and `AsPageIter` for `VBox<T>`.

## Control Flow, State, and Persistence
Construction allocates with allocator `A` and GFP flags, then initializes or leaves memory uninitialized. `pin_slice()` builds a vector with capacity, initializes elements in place with pin-init callbacks, then converts raw parts into a boxed slice. Drop first drops the contained value and then frees memory using `Layout::for_value`. Foreign ownership transfers raw pointers across C/Rust boundaries without dropping until reconstructed. Persistent state is the heap allocation and initialized value owned by the box; zero-sized types use dangling aligned pointers rather than real allocations.

## Dependencies and Integration
Depends on the allocator trait, `Kmalloc`/`Vmalloc`/`KVmalloc`, `Vec`, `Layout`, `MaybeUninit`, `Pin`, `pin_init` traits, `ForeignOwnable`, formatting traits, and page iteration support. It is the primary single-owner heap abstraction for Rust kernel code.

## Risks and Test Signals
Risks include unsafe `from_raw()` allocator mismatches, `assume_init()` on uninitialized memory, pinning violations through raw pointers, allocation leaks via `leak()` or `into_raw()`, incorrect unsized layout freeing, and panic/error cleanup during `pin_slice()`. Test signals are doctests, KUnit allocator tests, Miri-like reasoning for initialization, FFI round trips through `ForeignOwnable`, drop-order checks, ZST cases, trait-object coercions, and `VBox` page iteration.
