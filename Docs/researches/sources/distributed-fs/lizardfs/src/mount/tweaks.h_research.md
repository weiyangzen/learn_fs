## sources/distributed-fs/lizardfs/src/mount/tweaks.h

Purpose: declares the `Tweaks` runtime variable registry and global `gTweaks`.

Important APIs: registration overloads for atomic bool/uint32_t/uint64_t, `setValue(name, value)`, and `getAllValues()`.

Integration: read/write special inode uses it for operator-visible configuration; `readdata.cc` registers read/cache timeout and counter variables.

Risks and tests: registry lifetime is global; variables are stored by pointer, so registered atomics must outlive the registry entry. Tests should cover lifetime and duplicate names if expanded.
