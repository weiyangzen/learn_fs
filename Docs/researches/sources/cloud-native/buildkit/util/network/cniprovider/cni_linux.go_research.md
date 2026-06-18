## sources/cloud-native/buildkit/util/network/cniprovider/cni_linux.go

Purpose: Linux-specific CNI namespace sampling, RootlessKit detached-netns entry, and namespace-aware outbound dialing.

Important functions: `(*cniNS).sample`, `readFileAt`, `withDetachedNetNSIfAny`, `DialContext`, `dialer`, `isLoopbackHost`, `dialInNS`, `dialInNetNS`.

Control flow: `sample` opens `/sys/class/net/<veth>/statistics`, reads tx/rx counters with `openat`, parses int64 values, and updates `prevSample`. Detached-netns wrapper checks `$ROOTLESSKIT_STATE_DIR/netns` with `os.OpenRoot` and runs the callback via CNI `netns.WithNetNSPath` with context marker. `DialContext` captures current namespace for loopback DNS and dials inside the target namespace with `FallbackDelay=-1` to avoid Happy Eyeballs goroutine namespace escapes. Resolver `Dial` uses caller namespace for loopback resolver addresses and target namespace otherwise.

State/persistence: reads sysfs counters; temporarily switches OS thread netns during dial/listen operations. Dependencies: CNI plugins netns package, syscall, Go net resolver.

Integration points: `cniNS` implements `network.Dialer` for proxy egress and resource sampling. Risks: namespace switching requires careful OS-thread pinning handled by dependency; sysfs veth disappearance returns nil sample; custom resolver logic is subtle around loopback DNS. Test signals: `cni_linux_test.go` targets dial namespace escape prevention, in-namespace dialing, loopback DNS, and loopback host classification.
