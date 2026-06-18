# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/custom_sec_handlers.c

## Purpose
Tests libbpf custom SEC handler registration, setup/preload/attach callbacks, fallback handlers, and overriding built-in-like prefixes.

## Important APIs, types, and functions
Uses `libbpf_register_prog_handler()`, `libbpf_unregister_prog_handler()`, `libbpf_prog_handler_opts`, generated `test_custom_sec_handlers.skel.h`, callback cookies, `bpf_program__attach_raw_tracepoint()`, and `bpf_program__attach_tracepoint()`. Constructor registers `abc`, `abc/`, and `custom+`; destructor unregisters them. Runtime registers `kprobe+` and fallback NULL handler.

## Control flow and state
Callbacks alter autoload (`abc1` disabled), set `BPF_F_SLEEPABLE` for fallback, and attach selected custom programs. The test opens skeleton, validates inferred program types/autoload, loads, auto-attaches, verifies an unsupported manual attach error, triggers with sleep, and checks BSS called flags. Global state is handler IDs and callback cookies.

## Dependencies and integration points
Depends on libbpf section handler API and generated skeleton section names. It is tightly integrated with libbpf loader behavior, including fallback matching order.

## Risks and test signals
Handler registration is global process state; cleanup correctness matters. Passing signals include positive handler IDs, expected program types/autoload, successful load/attach, `EOPNOTSUPP` for unsupported attach, called flags true only for auto-attached sections, and unregister success.
