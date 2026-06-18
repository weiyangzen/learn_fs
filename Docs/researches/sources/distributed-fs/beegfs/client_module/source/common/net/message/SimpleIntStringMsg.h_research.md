# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.h

## Research
`SimpleIntStringMsg.h` declares a reusable `NetMessage` wrapper containing `intValue`, `strValue`, and `strValueLen`. Inline constructors initialize the base type and optionally bind a caller-provided string reference, measuring length with `strlen`. Accessors return the integer and string pointer.

Control flow is construction/access only. State is partly non-owning: the string must outlive serialization, and deserialized strings are receive-buffer slices. Dependencies are `NetMessage.h` and the ops object from the `.c` file. Integration points are generic response/control messages that need a numeric code and explanatory string without custom payload code. Risks include dangling string pointers, not preserving embedded NULs when initialized from C strings, and confusing buffer-slice lifetime after request handling. Test signals are response handlers reading both fields before freeing receive buffers and serializers producing the expected int-then-string wire order.
