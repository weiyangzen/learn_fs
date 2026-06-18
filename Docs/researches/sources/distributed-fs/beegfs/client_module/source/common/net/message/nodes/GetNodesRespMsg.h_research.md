# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.h

## Research
`GetNodesRespMsg.h` declares the receive-side node-list response. It embeds `NetMessage`, stores root owner metadata and a raw serialized node list, initializes with `NETMSGTYPE_GetNodesResp`, and provides `GetNodesRespMsg_parseNodeList` to convert the raw list into a `NodeList` using app context.

Control flow is init, deserialization, then explicit caller-triggered parse. State in `rawNodeList` references the receive buffer until parsed; `rootNumID` defaults to zero. Dependencies include `NetMessage.h` and `NodeList.h`. Integration points are node stores, root owner setup, and client startup/sync paths. Risks are forgetting to call `parseNodeList`, using raw data after buffer lifetime ends, and missing serialization support. Test signals are node discovery populating stores and root owner fields matching server responses.
