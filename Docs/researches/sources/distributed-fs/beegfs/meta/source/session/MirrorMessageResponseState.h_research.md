## sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.h

Purpose: declares the polymorphic base and common response-state templates used by mirrored message processing.

Important APIs/types: `MirroredMessageResponseState` requires `sendResponse`, `changesObservableState`, `serializerTag`, and `serializeContents`. `ErrorCodeResponseState<RespMsgT, SerializerTag>` stores an `FhgfsOpsErr` and sends either a generic indirect communication error or `RespMsgT(result)`. `ErrorAndEntryResponseState<RespMsgT, SerializerTag>` additionally stores `EntryInfo` and sends `RespMsgT(result, &info)`.

Control flow: concrete message response states either derive directly from the base or use these templates. Common templates deserialize by reading result and optional `EntryInfo`, serialize the same fields, and report observable changes only on `FhgfsOpsErr_SUCCESS`.

State and persistence behavior: response state is serialized into session mirror state slots. This is process and restart relevant because sessions can be saved and loaded.

Dependencies and integration points: depends on `GenericResponseMsg`, `EntryInfo`, `Serializer`, `Deserializer`, and net-message response contexts. Used by many `*MsgEx` mirrored message classes.

Risks: `changesObservableState` equates success with observable mutation, which may be too coarse for messages that succeed without mutation or fail after partial mutation unless they provide custom response states. Communication errors are normalized to a generic response instead of the specific response message type.

Test signals: test result serialization, communication-error response mapping, success/failure observable-state semantics, and derived custom response states with the deserializer factory.
