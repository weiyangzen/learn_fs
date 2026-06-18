# sources/distributed-fs/ceph-client/net/bluetooth/eir.c

## Purpose
This file constructs and parses Bluetooth Extended Inquiry Response and LE advertising data, including local names, appearance, service UUID lists, service data, advertising payloads, scan responses, and periodic advertising data.

## Important APIs, Types, And Functions
Public functions include `eir_create()`, `eir_create_adv_data()`, `eir_create_scan_rsp()`, `eir_create_per_adv_data()`, `eir_append_local_name()`, `eir_append_appearance()`, `eir_append_service_data()`, and `eir_get_service_data()`. Internal helpers create 16-bit, 32-bit, and 128-bit UUID lists from `hdev->uuids`.

## Control Flow
Classic EIR creation appends a complete or shortened device name, inquiry TX power, device ID, and UUID lists until `HCI_MAX_EIR_LENGTH` space runs out. Advertising creation locates an optional advertising instance, conditionally adds flags based on instance and global discoverability, copies user-provided advertising data, and optionally appends TX power. Scan response creation either builds a default appearance/name response or combines instance scan response data with managed appearance/local-name fields. Service-data lookup iterates AD elements of type `EIR_SERVICE_DATA` and returns the matching UUID payload.

## State, Persistence, And Dependencies
The file reads state from `struct hci_dev`, `struct adv_info`, management advertising flags, UUID lists, names, appearance, power values, and device ID fields. It writes only caller-provided output buffers and has no persistent state.

## Integration Points
HCI setup and management advertising code use these helpers when programming controller EIR/advertising/scan-response data. It integrates with `hci_find_adv_instance()`, `hci_adv_instance_flags()`, `mgmt_get_adv_discov_flags()`, and EIR constants from Bluetooth headers.

## Risks
Most append helpers assume the caller has already reserved enough space; only selected paths check remaining size. Instance advertising data is memcpy'd using stored lengths, so earlier validation in management paths is required. UUID list truncation correctly changes the type from ALL to SOME, but boundary tests are important. Service-data parsing must avoid underflow when malformed fields have less than UUID length.

## Test Signals
Signals include generated EIR/AD bytes matching expected length/type/value encoding, truncation switching UUID list types to SOME, advertising flags respecting managed/discoverable/no-BR-EDR rules, scan responses containing requested appearance/name data, and malformed EIR data not causing out-of-bounds access.
