<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c

## Purpose

`sigaltstack.c` tests x86 signal alternate-stack minimum-size behavior. It validates that too-small altstacks are rejected or fail safely, and that the kernel-reported `AT_MINSIGSTKSZ` is usable for signal delivery.

## Important APIs, Types, and Functions

`setup_altstack()` wraps `sigaltstack()`. `sigsegv()` catches expected delivery failures with `longjmp()`. `sigalrm()` confirms successful alternate-stack signal delivery. `test_sigaltstack()` configures a candidate stack, arms handlers, raises or alarms into the stack, and checks whether the result matches expectations. `main()` reads `getauxval(AT_MINSIGSTKSZ)` and exercises enforced and auxv-derived sizes.

## Control Flow and State

The test uses globals `nerrs`, `sigalrm_expected`, `at_minstack_size`, and `jmpbuf`. Each case installs an altstack, triggers a signal, and either observes normal handler execution or a controlled `SIGSEGV`. State is process-local and reset between cases.

## Dependencies and Integration Points

It depends on libc signal APIs, auxv support, x86 signal-frame sizing, and the kselftest environment. It is sensitive to kernel XSAVE feature size because enabled xstate increases required signal-frame space.

## Risks and Test Signals

Risks include accepting altstacks below the architecture-enforced minimum, underreporting `AT_MINSIGSTKSZ`, or corrupting delivery when large xstate is enabled. Passing output shows expected signal delivery on adequate stacks and expected rejection or safe failure for inadequate stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c -->
