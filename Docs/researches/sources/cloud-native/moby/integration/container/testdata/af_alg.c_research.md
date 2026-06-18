# sources/cloud-native/moby/integration/container/testdata/af_alg.c

Purpose: C fixture used by `exec_afalg_linux_test.go` to attempt creation and use of an `AF_ALG` socket inside a container.

Important APIs and flow: The program creates a `socket(AF_ALG, SOCK_SEQPACKET, 0)`, binds it to a `sockaddr_alg` requesting SHA1 hash, accepts an operation socket, writes `hello world`, reads the hash, prints success, and exits. Each syscall failure prints with `perror` and returns nonzero.

State and dependencies: It has no persistent state; it allocates two file descriptors and closes them. It depends on Linux kernel crypto socket headers and runtime permission to create AF_ALG sockets.

Risks and signals: In the security test, successful execution would be a failure because default container policy should deny AF_ALG for unprivileged users. The fixture provides a realistic socket path beyond mere `socket()` creation by exercising bind/accept/read/write if allowed.
