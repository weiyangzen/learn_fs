<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go

## Purpose
FreeBSD implementation hooks for libnetwork default gateway network.

## Important APIs, Types, And Functions
Defines `libnGWNetwork = "docker_gwbridge"`, returns no platform endpoint option, and leaves `Controller.createGWNetwork` unimplemented with `errdefs.NotImplemented`.

## Control Flow
Calls that require gateway network creation fail with not implemented on FreeBSD.

## State And Persistence
No state is created by this file.

## Dependencies And Integration Points
Allows common gateway code to compile while signaling unsupported behavior.

## Risks And Edge Cases
Sandboxes that require a dynamically created default gateway network will fail on FreeBSD.

## Test Signals
FreeBSD build and expected not-implemented behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go -->
