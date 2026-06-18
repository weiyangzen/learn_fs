# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_types.h

## Purpose
This generated header defines the reduced H.323/H.225/H.245 ASN.1 object model consumed by the H.323 conntrack decoder and NAT helper. It maps ASN.1 SEQUENCE and CHOICE nodes into C structs, enums, option bitmasks, and fixed-size arrays.

## Important APIs, Types, and Functions
Key address and media types include `TransportAddress`, `H245_TransportAddress`, `UnicastAddress`, `DataProtocolCapability`, `DataApplicationCapability`, `DataType`, `H2250LogicalChannelParameters`, `OpenLogicalChannel`, `OpenLogicalChannelAck`, and `NetworkAccessParameters`. Q.931/H.225 UUIE types include `Setup_UUIE`, `CallProceeding_UUIE`, `Connect_UUIE`, `Alerting_UUIE`, `Facility_UUIE`, `Progress_UUIE`, `H323_UU_PDU`, and `H323_UserInformation`. RAS types include gatekeeper, registration, unregistration, admission, location, info-response, and top-level `RasMessage` structures.

## Control Flow
The decoder fills these structures according to ASN.1 choices and option bits. Helper code checks `choice` discriminants and option masks to find embedded control addresses, media channels, fast-start logical channels, RAS addresses, and time-to-live values. Fixed arrays cap fast-start/control entries at 30, H.245 control entries at 4, and some RAS address arrays at 10.

## State and Persistence
The structures are transient decoded representations, not persistent state. Options are represented as high-bit masks, and choices are represented by enum discriminants plus unions. No allocation or global mutable state is declared.

## Dependencies and Integration Points
It is included by the ASN.1 decoder and H.323 conntrack helper. Field names and limits must match generated decoder tables and NAT traversal logic.

## Risks
Unsupported ASN.1 alternatives are represented only as choices without payloads. Fixed array caps can truncate or reject large messages. The file contains a duplicate `typedef struct H323_UserInformation` line, which is unusual and should be watched for compiler tolerance. IPv6 address structs use `unsigned int`, reflecting limited support rather than a complete IPv6 representation. Changing enum order or option bits would break decoder compatibility.

## Test Signals
Compile the H.323 helper with strict warnings, decode representative H.225/Q.931/RAS/H.245 messages, validate fast-start and H.245 control array bounds, test all address-bearing message types used by NAT, and fuzz CHOICE/option combinations to ensure helpers ignore unsupported alternatives safely.
