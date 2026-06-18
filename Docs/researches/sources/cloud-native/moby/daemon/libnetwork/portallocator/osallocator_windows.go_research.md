<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go

Purpose: Windows OS-backed port allocation by creating dummy listeners to reserve host ports.

Important APIs/types/functions: `ErrPortMappedForIP` and `ErrPortNotMapped` describe mapping state failures. `OSAllocator` stores `osListeners map[types.Protocol]map[netip.AddrPort]io.Closer`, a lock, and a logical `PortAllocator`. `New` constructs it. `AllocateHostPort` reserves a logical port and creates a TCP, UDP, or SCTP listener through `allocateHostPort`. `Deallocate` closes and removes the listener and releases the logical reservation.

Control flow: allocation locks the allocator, gets a logical port, validates host IP, checks duplicate `proto/address/port`, then opens a listener with protocol version selected from host IP family. On error it releases logical state and closes any partial listener. Deallocation validates the key, closes the listener if present, deletes map state, and releases the port.

State and persistence: in-memory listener map plus OS listener handles. No on-disk persistence.

Dependencies and integration points: uses Go `net` TCP/UDP listeners, SCTP library, libnetwork `types.Protocol`, and the shared logical allocator. It is a Windows counterpart to Linux socket reservation but without Linux cBPF filter behavior.

Risks and test signals: listener leaks or missed logical releases can permanently block ports in the daemon. Duplicate detection is per `netip.AddrPort` and protocol. Direct tests are not in this subset; behavior is validated by Windows build/test coverage and consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go -->
