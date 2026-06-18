# sources/cloud-native/moby/integration/container/testdata/af_vsock.c

Purpose: Minimal C fixture used to verify `AF_VSOCK` socket creation is blocked inside a default Linux container.

Important APIs and flow: The program calls `socket(AF_VSOCK, SOCK_STREAM, 0)`, reports any error with `perror("socket")`, prints success if the socket is created, closes the descriptor, and exits.

State and dependencies: No persistence; one file descriptor is created if allowed. It depends on `<linux/vm_sockets.h>` and the kernel supporting the address family.

Risks and signals: The integration test expects this binary to fail as UID 1000 under default seccomp. If it succeeds, container isolation may allow guest/host vsock access unexpectedly. If compilation fails, the test environment lacks the required Linux headers.
