# sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc.h

Purpose: Defines USB Communications Device Class constants, functional descriptors, requests, notifications, and NCM/MBIM data structures.

Important APIs/types/functions: Constants cover CDC subclasses/protocols, functional descriptor types, ACM/call-management capabilities, class-specific requests, line coding, control-line bits, Ethernet packet filters, notifications, serial state bits, NCM NTB parameters, NTH/NDP signatures, datagram pointer entries, MBIM signatures, NCM capabilities, NTB formats, and CRC modes. Structs model header, call management, ACM, union, country, network terminal, Ethernet, DMM, MDLM/detail, OBEX, NCM, MBIM and extended MBIM descriptors, line coding, notifications, speed-change notifications, NCM parameter blocks, NTH16/NTH32, NDP16/NDP32, DPE16/DPE32, and NCM input-size negotiation.

Control flow: During enumeration, host drivers parse descriptors to bind ACM, Ethernet, NCM, MBIM, or other CDC functions. Runtime control requests configure line coding, control line state, Ethernet filters, NTB format/input size, datagram size, CRC mode, and encapsulated commands. Interrupt notifications report network, serial, response, or speed changes.

State and persistence behavior: Descriptors are static capability data. Runtime state includes line coding, DTR/RTS, packet filters, NTB format and input size, CRC mode, network connection, and NCM/MBIM transfer aggregation parameters.

Dependencies and integration points: Includes `linux/types.h`; integrates with USB core, CDC ACM, cdc_ether, cdc_ncm, cdc_mbim, modem-management stacks, and gadget implementations.

Risks: NCM/MBIM structures are wire-format and alignment-sensitive. NTB length/index validation is security-critical. Descriptor capability bits and request availability must match device behavior.

Test signals: Enumerate descriptor variants, negotiate line coding/control lines, exercise Ethernet packet filters, NCM NTB16/NTB32 aggregation, MBIM IPS/DSS sessions, notification parsing, and malformed descriptor/NTB fuzzing.
