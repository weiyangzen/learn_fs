# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2_user.c

## Research

This user-space helper loads and attaches a LIRC mode2 BPF program to an rc-loopback LIRC device, then validates decoded events through the associated input event device. It is the executable backend for `test_lirc_mode2.sh`.

The program expects `/dev/lircN` and `/dev/input/eventM`. It loads `test_lirc_mode2_kern.bpf.o` as `BPF_PROG_TYPE_LIRC_MODE2`, opens the LIRC FD read/write nonblocking and the input FD read-only nonblocking, checks that detach before attach returns `-ENOENT`, queries attached programs, attaches with `bpf_prog_attach(..., BPF_LIRC_MODE2, 0)`, writes raw IR values `0x1dead` and `0x20101`, and polls/reads input events until it observes `EV_MSC/MSC_SCAN/0xdead` and `EV_REL/REL_Y/1`. It then verifies exactly one attached program is reported and detaches it.

Runtime state includes the LIRC FD, input event FD, loaded BPF object/program FD, program attachment state, and transient IR/input event buffers. Cleanup relies on process exit and explicit detach at the end; no repository state is persisted. Dependencies include the kernel LIRC and input subsystems, rc-loopback device nodes, permissions to access both devices, and the compiled BPF object expected by the helper.

Risks are kernel/device timing sensitivity and infinite polling loops if expected events never arrive. Device drivers can differ in accepted sample formats, reads may fail with nonblocking behavior, and missing LIRC attach support will fail even though the test source is correct. Test signals are successful load/query/attach/detach, successful raw IR writes, expected input events, and nonzero exit on any syscall/libbpf mismatch.
