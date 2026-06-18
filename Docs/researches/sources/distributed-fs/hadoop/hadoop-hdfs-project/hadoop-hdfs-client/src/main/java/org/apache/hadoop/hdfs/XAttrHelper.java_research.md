# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/XAttrHelper.java

Purpose: `XAttrHelper` centralizes HDFS extended-attribute name parsing, prefix formatting, list construction, and map conversion. It is private client-side support for xattr APIs.

Important APIs/types/functions: `buildXAttr(String)`, `buildXAttr(String,byte[])`, `buildXAttrAsList(String)`, `getFirstXAttrValue(List<XAttr>)`, `getFirstXAttr(List<XAttr>)`, `buildXAttrMap(List<XAttr>)`, `getPrefixedName(XAttr)`, `getPrefixedName(NameSpace,String)`, and `buildXAttrs(List<String>)`.

Control flow: `buildXAttr` validates non-null names, requires a prefix followed by a dot, rejects empty local names, maps case-insensitive prefixes `user`, `trusted`, `system`, `security`, and `raw` to `XAttr.NameSpace`, and builds an `XAttr` with the substring after the dot. List and map helpers use the builder or prefixed-name conversion. Null xattr values are converted to empty byte arrays for API callers that need to distinguish existing-empty from missing.

State and persistence behavior: stateless utility class. It allocates lists/maps and `XAttr` objects but persists nothing.

Dependencies and integration points: uses `HadoopIllegalArgumentException`, `XAttr`, `XAttr.NameSpace`, Hadoop `Lists`, Guava-compatible `Maps`, `StringUtils`, and `Preconditions`. It feeds HDFS xattr RPC request/response conversion paths and user-facing xattr maps.

Risks: prefix matching is case-insensitive but generated names are lower-case namespace strings plus original local name. Empty values are normalized to `new byte[0]`, which callers must not confuse with absent xattrs (`null` return from `getFirstXAttrValue`). Tests should cover invalid prefixes, missing dot, empty local names, all namespace prefixes, case variants, null lists, empty lists, null values, and round-tripping prefixed names.
