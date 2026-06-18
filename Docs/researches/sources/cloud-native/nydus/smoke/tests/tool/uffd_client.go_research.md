# sources/cloud-native/nydus/smoke/tests/tool/uffd_client.go

## Purpose
This Linux-only helper implements a test client for Nydus UFFD block-device mode. It connects to the daemon's Unix socket, negotiates device stats and handshakes, manages a userfaultfd-backed memory mapping, handles zerocopy page-fault responses, and exposes read/verification helpers.

## Important APIs, Types, And Functions
Constants define protocol message types, policy IDs, syscall/ioctl numbers, and EROFS magic. Protocol structs model VMA regions, handshake, blob ranges, page-fault responses, stat request/response. `UffdClient` stores socket, userfaultfd, mmap slice, device metadata, policy, region, worker synchronization, and close state. Syscall helpers include `sysUserfaultfd`, `createUserfaultfd`, `uffdRegister`, `uffdWake`, `sendWithFd`, and `recvWithFd`. `NewUffdClient` connects and requests stats. `Handshake` creates/registers mmap memory and sends the userfaultfd via SCM_RIGHTS. `zerocopyWorker` maps blob fds into the region on page-fault responses. `ReadAt`, `Close`, `VerifyErofsMagic`, `VerifyNonZero`, `closeFds`, `isTemporaryError`, and `ExportDiskImage` provide test-facing operations.

## Control Flow
A test creates the client, reads device size/block size from a stat exchange, handshakes in copy or zerocopy mode, then reads from the mapped memory. In zerocopy mode a goroutine receives page-fault responses and maps file descriptors at requested offsets before waking userfaultfd waiters. Close signals the worker, closes the socket, unmaps memory, and closes fds.

## State And Persistence
The client creates kernel userfaultfd state, an anonymous mmap region rounded to 2 MiB alignment, Unix socket connections, and transient file descriptor transfers. `ExportDiskImage` writes a raw disk image using `nydus-image export --block`.

## Dependencies And Integration Points
It depends on Linux userfaultfd, Unix SCM_RIGHTS, architecture-specific syscall numbers, Nydus UFFD protocol JSON, `nydusd uffd`, and `nydus-image export`. It is used by `uffd_test.go`.

## Risks
The build tag restricts this to Linux, but userfaultfd may be disabled by kernel policy. Unsafe mmap slicing and fixed syscall numbers are inherently platform-sensitive. Zerocopy worker silently ignores malformed responses or mmap failures, which can later appear as read/verification failures.

## Test Signals
Signals include successful stat response, handshake, EROFS magic reads, nonzero/expected data reads, and clean resource shutdown.
