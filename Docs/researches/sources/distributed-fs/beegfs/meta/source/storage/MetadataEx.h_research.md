## sources/distributed-fs/beegfs/meta/source/storage/MetadataEx.h

Purpose: Defines metadata-server storage constants shared by metadata serialization and on-disk extended-attribute handling. It names the temporary metadata update suffix, the BeeGFS metadata xattr, and the remote-storage-target xattr.

Important APIs/types/functions: The exported constants are `META_UPDATE_EXT_STR`, `META_XATTR_NAME`, `RST_XATTR_NAME`, `METADATA_XATTR_NAME_LIST`, and `META_SERBUF_SIZE`. `METADATA_XATTR_NAME_LIST` is the authoritative list of non-user metadata attributes that buddy metadata resync must copy.

Control flow: Header-only constants; no runtime control flow.

State and persistence: The constants describe persistent xattr names on metadata entries and the serialized metadata buffer size used for transfer/copy operations. The maintainer warning is important: adding a metadata xattr without extending `METADATA_XATTR_NAME_LIST` can leave mirrored metadata inconsistent.

Dependencies and integration: Includes common metadata definitions and is consumed by metadata storage/resync code that reads, writes, serializes, or mirrors dentries and inode metadata.

Risks and test signals: Primary risk is schema drift between persisted xattrs and the hard-coded resync list. Regression tests should exercise buddy metadata resync with every system metadata xattr and buffer-size limits around `META_SERBUF_SIZE`.
