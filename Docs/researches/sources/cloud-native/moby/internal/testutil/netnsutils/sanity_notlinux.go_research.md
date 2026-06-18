<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go

Purpose: no-op implementation of `AssertSocketSameNetNS` for non-Linux platforms. It preserves the call surface without attempting unavailable Linux namespace checks. State and control flow are absent. Dependencies are `syscall` and `testing` for signature compatibility. Risks are only that non-Linux tests receive no namespace sanity validation. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go -->
