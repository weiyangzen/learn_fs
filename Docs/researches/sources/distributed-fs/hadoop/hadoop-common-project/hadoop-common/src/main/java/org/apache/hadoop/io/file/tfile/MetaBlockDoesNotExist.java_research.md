# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockDoesNotExist.java

Purpose: checked exception indicating a named meta block is absent.

Important APIs/types/functions: class extends `IOException`; package-private constructor accepting a message.

Control flow: `BCFile.Reader.getMetaBlock()` throws it when `MetaIndex.getMetaByName()` returns null.

State and persistence: exception instance only.

Dependencies and integration: public stable API type for TFile/BCFile readers.

Risks: callers must distinguish absent optional metadata from file corruption or I/O failures. Tests should verify missing meta block lookup throws this subtype and that existing meta blocks open normally.
