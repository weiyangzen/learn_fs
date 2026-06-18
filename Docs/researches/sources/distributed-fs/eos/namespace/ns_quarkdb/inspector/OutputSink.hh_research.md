# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.hh

## Purpose
This header defines the abstract inspector output interface and concrete stream-oriented sinks. It separates inspector command logic from textual and JSON formatting.

## Important APIs, Types, and Functions
`OutputSink` stores `mOut` and `mErr` references, requires subclasses to implement `print(const std::map<std::string,std::string>&)`, and provides default string, JSON, error, file-protobuf, and container-protobuf print overloads. `StreamSink` prints key-value records. `JsonStreamSink` prints one JSON array over its lifetime. `JsonLinedStreamSink` prints newline-delimited JSON and overrides direct `Json::Value` printing.

## Control Flow
Inspectors call a high-level `print()` overload with protobufs or maps. The base class builds map rows in the implementation file and calls the virtual map function. Direct string output is escaped and newline-terminated. Direct JSON output defaults to jsoncpp stream formatting unless overridden by JSON-lines.

## State and Persistence Behavior
The header owns no namespace state. It defines output stream references and, for JSON sinks, framing/writer state. Because `JsonStreamSink` closes the JSON array in its destructor, object lifetime is part of the emitted format contract.

## Dependencies and Integration Points
It includes scanners, printing options, protobuf declarations, jsoncpp, and EOS namespace macros. It is injected into `Inspector`, allowing command code to stay independent of output format.

## Risks and Test Signals
Subclasses must be kept alive until all output is complete, especially `JsonStreamSink`. Tests should verify polymorphic dispatch for map rows, default string escaping, direct JSON printing behavior for both JSON sink types, and valid array output when zero or many records are printed.
