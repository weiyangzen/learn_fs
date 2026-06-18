# sources/cloud-native/moby/daemon/libnetwork/netutils/utils.go

## Purpose
General network utility functions for MAC generation, random interface/name generation, reverse-DNS key formatting, IPv6 listenability probing, and MAC parsing.

## Important APIs, Types, And Functions
`GenerateMACFromIP` returns a locally administered MAC with OUI-like prefix `02:42` and IPv4-derived suffix when an IP is provided. `GenerateRandomMAC` uses crypto randomness and fixes multicast/local bits. `GenerateRandomName` joins a prefix with random hex to an exact length. `ReverseIP` reverses canonical IPv4 or IPv6 text into dotted form for PTR maps. `IsV6Listenable` caches whether `[::1]:0` can be listened on. `MustParseMAC` panics on invalid MAC strings.

## Control Flow
Random functions fill byte slices via `crypto/rand`. `ReverseIP` branches on `To4`; IPv6 handling expands compressed groups, pads to four hex digits, reverses nibbles, and joins with dots. `IsV6Listenable` uses `sync.Once` to perform a single TCP6 listen probe and cache the result.

## State And Persistence
Only `v6ListenableCached` and `v6ListenableOnce` persist process-local state. Generated values are not stored here but feed endpoint/interface configuration elsewhere.

## Dependencies And Integration Points
Used by endpoint creation for random MACs, DNS service reverse maps in `network.go`, Linux interface-name generation, and bridge tests that adjust expectations based on IPv6 support.

## Risks
`rand.Read` errors in MAC generation are ignored in two helpers, which matches prior behavior but can theoretically produce low-quality values on entropy failure. `ReverseIP` assumes canonical strings and is not a full DNS `arpa` formatter. `MustParseMAC` is appropriate only for constants or tests.

## Test Signals
Linux tests cover random name boundaries, uniqueness sampling, random MAC inequality, and the Linux reserved-network helpers; reverse-IP behavior is indirectly exercised through DNS service records.
