# sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.h

## Purpose
This header declares the HCI codec discovery and cleanup helpers.

## Important APIs, Types, And Functions
It declares `hci_read_supported_codecs()`, `hci_read_supported_codecs_v2()`, and `hci_codec_list_clear()`.

## Control Flow
There is no executable control flow. The declarations let HCI setup code select the correct discovery command version and clear codec state during teardown or reset.

## State, Persistence, And Dependencies
State is owned by the caller-provided `struct hci_dev` and its codec list. The header assumes `struct hci_dev` and `struct list_head` are visible to includers.

## Integration Points
HCI core includes this header for controller codec enumeration, especially for SCO/ISO/audio capability reporting paths.

## Risks
Because the header is intentionally small and lacks include guards, it depends on identical repeated declarations being harmless. Callers must hold any required HCI device context expected by the implementation.

## Test Signals
Compile coverage catches signature drift; runtime discovery tests are in `hci_codec.c` consumers.
