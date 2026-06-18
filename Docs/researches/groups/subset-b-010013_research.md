# subset-b-010013 Research

Grouped source research for SMBJ MS-FSCC file information records, FSCTL named-pipe helpers, SMB1 negotiate shim code, and SMB2/SMB3 packet/message serialization. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAlignmentInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAlignmentInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAlignmentInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file AlignmentInformation` records. The source was read as a complete 29-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileAlignmentInformation implements FileQueryableInformation`; state fields: `alignmentRequirement`; methods: `getAlignmentRequirement`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAlignmentInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java` is an aggregate MS-FSCC `FileAllInformation` value object combining basic, standard, internal, EA, access, position, mode, alignment, and name data from a single query-info response. The source was read as a complete 76-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileAllInformation implements FileQueryableInformation`; state fields: `basicInformation`, `standardInformation`, `internalInformation`, `eaInformation`, `accessInformation`, `positionInformation`, `modeInformation`, `alignmentInformation`, `nameInformation`; methods: `getBasicInformation`, `getStandardInformation`, `getInternalInformation`, `getEaInformation`, `getAccessInformation`, `getPositionInformation`, `getModeInformation`, `getAlignmentInformation`, `getNameInformation`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllocationInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllocationInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllocationInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file AllocationInformation` records. The source was read as a complete 29-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileAllocationInformation implements FileSettableInformation`; state fields: `allocationSize`; methods: `getAllocationSize`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllocationInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBasicInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBasicInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBasicInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file BasicInformation` records. The source was read as a complete 64-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileBasicInformation implements FileQueryableInformation, FileSettableInformation`; state fields: `DONT_SET`, `DONT_UPDATE`, `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `fileAttributes`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getFileAttributes`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBasicInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBothDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBothDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBothDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 80-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileBothDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`, `eaSize`, `shortName`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`, `getEaSize`, `getShortName`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileBothDirectoryInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 68-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryQueryableInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryQueryableInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryQueryableInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file DirectoryQueryableInformation` records. The source was read as a complete 40-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public abstract class FileDirectoryQueryableInformation implements FileInformation`; state fields: `fileName`, `nextOffset`, `fileIndex`; methods: `getNextOffset`, `getFileIndex`, `getFileName`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDirectoryQueryableInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDispositionInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDispositionInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDispositionInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file DispositionInformation` records. The source was read as a complete 32-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileDispositionInformation implements FileSettableInformation`; state fields: `deleteOnClose`; methods: `isDeleteOnClose`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileDispositionInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEaInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEaInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEaInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file EaInformation` records. The source was read as a complete 28-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileEaInformation implements FileQueryableInformation`; state fields: `eaSize`; methods: `getEaSize`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEaInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEndOfFileInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEndOfFileInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEndOfFileInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file EndOffile Information` records. The source was read as a complete 32-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileEndOfFileInformation implements FileSettableInformation`; state fields: `endOfFile`; methods: `getEndOfFile`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileEndOfFileInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileFullDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileFullDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileFullDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 74-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileFullDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`, `eaSize`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`, `getEaSize`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileFullDirectoryInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdBothDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdBothDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdBothDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 87-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileIdBothDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`, `eaSize`, `shortName`, `fileId`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`, `getEaSize`, `getShortName`, `getFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdBothDirectoryInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 81-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileIdFullDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`, `eaSize`, `fileId`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`, `getEaSize`, `getFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java` defines a marker or codec contract for MS-FSCC file information records used by SMB2 query and set-info paths. The source was read as a complete 36-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public interface FileInformation`; notable imports: `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

There is no runtime branch logic; implementors are selected by `FileInformationFactory` and then encoded into or decoded from SMB buffers.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java` is the central MS-FSCC file-information codec registry. It maps SMB file information POJOs to their `FileInformationClass` values, parses QUERY_INFO and QUERY_DIRECTORY buffers, encodes set-info payloads, and iterates variable-length directory result chains using `NextEntryOffset`. The source was read as a complete 705-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileInformationFactory`; state fields: `encoders`, `decoders`, `buffer`, `decoder`, `offsetStart`, `next`; methods: `getInformationClass`, `read`, `write`, `getEncoder`, `getDecoder`, `parseFileInformationList`, `createFileInformationIterator`, `hasNext`, `next`, `prepareNext`, `remove`, `parseFileAllInformation`, `parseFileNameInformation`, `parseFileBasicInformation`, `parseFileStandardInformation`, `parseFileInternalInformation`, `parseFileEaInformation`, `parseFileStreamInformation`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Endian`, `com.hierynomus.smbj.common.SMBRuntimeException`, `java.util.*`.

## Control Flow

Static initialization registers decoder and encoder instances by Java class. Public callers obtain a codec with `getEncoder` or `getDecoder`; parse helpers then read fields in MS-FSCC wire order from a little-endian `Buffer`. Directory listings use `FileInfoIterator`, which seeks to `offsetStart`, decodes one entry, advances by `NextEntryOffset`, and stops when that offset is zero.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Endian`, `com.hierynomus.smbj.common.SMBRuntimeException`, `java.util.*`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; UTF-16LE byte counts must remain even and must be counted as bytes on the wire, not Java characters; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; registry lookup coverage for every supported codec and rejection of unsupported classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInternalInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInternalInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInternalInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file InternalInformation` records. The source was read as a complete 28-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileInternalInformation implements FileQueryableInformation`; state fields: `indexNumber`; methods: `getIndexNumber`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInternalInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileLinkInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileLinkInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileLinkInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file LinkInformation` records. The source was read as a complete 23-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileLinkInformation extends FileRenameInformation`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileLinkInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileModeInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileModeInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileModeInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file ModeInformation` records. The source was read as a complete 29-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileModeInformation implements FileQueryableInformation, FileSettableInformation`; state fields: `mode`; methods: `getMode`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileModeInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileNamesInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileNamesInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileNamesInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 22-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileNamesInformation extends FileDirectoryQueryableInformation`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileNamesInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FilePositionInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FilePositionInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FilePositionInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file PositionInformation` records. The source was read as a complete 29-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FilePositionInformation implements FileQueryableInformation`; state fields: `currentByteOffset`; methods: `getCurrentByteOffset`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FilePositionInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileQueryableInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileQueryableInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileQueryableInformation.java` defines a marker or codec contract for MS-FSCC file information records used by SMB2 query and set-info paths. The source was read as a complete 19-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public interface FileQueryableInformation extends FileInformation`.

## Control Flow

There is no runtime branch logic; implementors are selected by `FileInformationFactory` and then encoded into or decoded from SMB buffers.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileQueryableInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileRenameInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileRenameInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileRenameInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file RenameInformation` records. The source was read as a complete 47-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileRenameInformation implements FileSettableInformation`; state fields: `replaceIfExists`, `rootDirectory`, `fileNameLength`, `fileName`; methods: `isReplaceIfExists`, `getRootDirectory`, `getFileNameLength`, `getFileName`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileRenameInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileSettableInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileSettableInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileSettableInformation.java` defines a marker or codec contract for MS-FSCC file information records used by SMB2 query and set-info paths. The source was read as a complete 19-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public interface FileSettableInformation extends FileInformation`.

## Control Flow

There is no runtime branch logic; implementors are selected by `FileInformationFactory` and then encoded into or decoded from SMB buffers.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileSettableInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStandardInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStandardInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStandardInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file StandardInformation` records. The source was read as a complete 52-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileStandardInformation implements FileQueryableInformation`; state fields: `allocationSize`, `endOfFile`, `numberOfLinks`, `deletePending`, `directory`; methods: `getAllocationSize`, `getEndOfFile`, `getNumberOfLinks`, `isDeletePending`, `isDirectory`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStandardInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file StreamInformation` records. The source was read as a complete 43-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileStreamInformation implements FileQueryableInformation`; state fields: `streamList`; methods: `getStreamList`, `getStreamNames`; notable imports: `java.util.ArrayList`, `java.util.List`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `java.util.ArrayList`, `java.util.List`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformationItem.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformationItem.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformationItem.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file StreamInformationItem` records. The source was read as a complete 41-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileStreamInformationItem`; state fields: `size`, `allocSize`, `name`; methods: `getSize`, `getAllocSize`, `getName`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformationItem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java` parses file-system level information returned by FSCC query-info calls and exposes it as immutable Java accessors. The source was read as a complete 128-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class ShareInfo`; state fields: `totalAllocationUnits`, `callerAvailableAllocationUnits`, `actualAvailableAllocationUnits`, `sectorsPerAllocationUnit`, `bytesPerSector`, `totalSpace`, `callerFreeSpace`, `actualFreeSpace`; methods: `getFreeSpace`, `getCallerFreeSpace`, `getTotalSpace`, `getTotalAllocationUnits`, `getAvailableAllocationUnits`, `getCallerAvailableAllocationUnits`, `getSectorsPerAllocationUnit`, `getBytesPerSector`, `parseFsFullSizeInformation`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/VolumeInfo.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/VolumeInfo.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/VolumeInfo.java` parses file-system level information returned by FSCC query-info calls and exposes it as immutable Java accessors. The source was read as a complete 116-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class VolumeInfo`; state fields: `volumeCreationTime`, `volumeSerialNumber`, `supportsObjects`, `volumeLabel`; methods: `parseFileFsVolumeInformation`, `getVolumeCreationTime`, `getVolumeSerialNumber`, `isSupportsObjects`, `getVolumeLabel`, `toString`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; UTF-16LE byte counts must remain even and must be counted as bytes on the wire, not Java characters.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/VolumeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java` parses the FSCTL_PIPE_PEEK response for named pipes, including pipe state, queued byte counts, message counts, and trailing payload data. The source was read as a complete 87-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FsCtlPipePeekResponse`; state fields: `STRUCTURE_SIZE`, `state`, `readDataAvailable`, `numberOfMessages`, `messageLength`, `data`, `value`; methods: `getState`, `getReadDataAvailable`, `getNumberOfMessages`, `getMessageLength`, `getData`, `read`, `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

`read` consumes fixed fields in order, maps the numeric pipe state through `EnumWithValue`, then reads the remaining bytes as peeked pipe data.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `SMB2IoctlRequest`/`SMB2IoctlResponse` and named-pipe helper code.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

named-pipe IOCTL round trips against a server plus golden buffer tests for fixed fields and UTF-16 names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java` writes the FSCTL_PIPE_WAIT request buffer used to wait for a named pipe by UTF-16LE name, optionally with a timeout. The source was read as a complete 80-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FsCtlPipeWaitRequest`; state fields: `timeoutUnit`, `name`, `timeout`, `timeoutSpecified`; methods: `getName`, `getTimeout`, `getTimeoutUnit`, `write`; notable imports: `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `java.util.concurrent.TimeUnit`.

## Control Flow

`write` emits the timeout as 100-nanosecond units when present, writes a timeout-present boolean, reserves padding, writes the UTF-16LE byte length, and appends the pipe name bytes.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `java.util.concurrent.TimeUnit`. It integrates with `SMB2IoctlRequest`/`SMB2IoctlResponse` and named-pipe helper code.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

named-pipe IOCTL round trips against a server plus golden buffer tests for fixed fields and UTF-16 names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1Header implements SMBHeader`; state fields: `headerStartPosition`, `messageEndPosition`; methods: `writeTo`, `readFrom`, `getHeaderStartPosition`, `getMessageEndPosition`, `setMessageEndPosition`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 25-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1NotSupportedException extends TransportException`; notable imports: `com.hierynomus.protocol.transport.TransportException`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.transport.TransportException`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Packet.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Packet.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Packet.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 48-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1Packet extends SMBPacket<SMB1PacketData, SMB1Header>`; methods: `write`, `writeTo`, `read`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Packet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketData.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 25-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1PacketData extends SMBPacketData<SMB1Header>`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 33-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1PacketFactory implements PacketFactory<SMB1PacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`.

## Control Flow

`read` wraps incoming bytes in `SMB1PacketData`; `canHandle` recognizes SMB1 by its protocol header bytes.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java` builds the legacy SMB1 COM_NEGOTIATE request that advertises SMB2 dialect strings to servers that expect negotiation to start with an SMB1-style packet. The source was read as a complete 74-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1ComNegotiateRequest extends SMB1Packet`; state fields: `dialects`; methods: `writeTo`, `read`, `toString`; notable imports: `com.hierynomus.mssmb.SMB1Packet`, `com.hierynomus.mssmb.SMB1PacketData`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

`writeTo` emits SMB1 negotiate parameters and dialect strings; `read` accepts the paired packet data path but performs no response parsing here.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb.SMB1Packet`, `com.hierynomus.mssmb.SMB1PacketData`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 28-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class DeadLetterPacketData extends SMBPacketData<SMBHeader>`; notable imports: `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smb.SMBPacketData`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smb.SMBPacketData`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ChangeNotifyFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ChangeNotifyFlags.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ChangeNotifyFlags.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 32-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ChangeNotifyFlags implements EnumWithValue<SMB2ChangeNotifyFlags>`; wire values: `WATCH_TREE`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ChangeNotifyFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 46-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CompletionFilter implements EnumWithValue<SMB2CompletionFilter>`; wire values: `FILE_NOTIFY_CHANGE_FILE_NAME`, `FILE_NOTIFY_CHANGE_DIR_NAME`, `FILE_NOTIFY_CHANGE_ATTRIBUTES`, `FILE_NOTIFY_CHANGE_SIZE`, `FILE_NOTIFY_CHANGE_LAST_WRITE`, `FILE_NOTIFY_CHANGE_LAST_ACCESS`, `FILE_NOTIFY_CHANGE_CREATION`, `FILE_NOTIFY_CHANGE_EA`, `FILE_NOTIFY_CHANGE_SECURITY`, `FILE_NOTIFY_CHANGE_STREAM_NAME`, `FILE_NOTIFY_CHANGE_STREAM_SIZE`, `FILE_NOTIFY_CHANGE_STREAM_WRITE`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompressionTransformHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompressionTransformHeader.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompressionTransformHeader.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 83-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CompressionTransformHeader implements SMBHeader`; state fields: `COMPRESSED_PROTOCOL_ID`, `headerStartPosition`, `originalCompressedSegmentSize`, `compressionAlgorithm`, `offset`, `messageEndPosition`; methods: `writeTo`, `readFrom`, `getHeaderStartPosition`, `getMessageEndPosition`, `getOriginalCompressedSegmentSize`, `getCompressionAlgorithm`, `getOffset`, `isCompressed`; notable imports: `java.util.Arrays`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`.

## Control Flow

`writeTo` emits the transform header; `readFrom` validates the transform protocol id, records start/end positions, and parses the algorithm/session/nonce or compression fields needed by encryption or decompression layers.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `java.util.Arrays`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompressionTransformHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateAction.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateAction.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateAction.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 54-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CreateAction implements EnumWithValue<SMB2CreateAction>`; wire values: `FILE_SUPERSEDED`, `FILE_OPENED`, `FILE_CREATED`, `FILE_OVERWRITTEN`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateDisposition.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateDisposition.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateDisposition.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 62-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CreateDisposition implements EnumWithValue<SMB2CreateDisposition>`; wire values: `FILE_SUPERSEDE`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateDisposition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 155-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CreateOptions implements EnumWithValue<SMB2CreateOptions>`; wire values: `FILE_DIRECTORY_FILE`, `FILE_WRITE_THROUGH`, `FILE_SEQUENTIAL_ONLY`, `FILE_NO_INTERMEDIATE_BUFFERING`, `FILE_NON_DIRECTORY_FILE`, `FILE_NO_EA_KNOWLEDGE`, `FILE_RANDOM_ACCESS`, `FILE_DELETE_ON_CLOSE`, `FILE_OPEN_FOR_BACKUP_INTENT`, `FILE_NO_COMPRESSION`, `FILE_OPEN_REPARSE_POINT`, `FILE_OPEN_NO_RECALL`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 46-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2DecryptedPacketData extends SMB2PacketData`; methods: `next`, `isDecrypted`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2Dialect`; wire values: `UNKNOWN`, `SMB_2_0_2`, `SMB_2_1`, `SMB_2XX`, `SMB_3_0`, `SMB_3_0_2`, `SMB_3_1_1`; state fields: `value`; methods: `getValue`, `isSmb3x`, `supportsSmb3x`, `lookup`; notable imports: `java.util.Set`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `java.util.Set`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 176-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Error`; state fields: `errorData`, `absolute`, `unparsedPathLength`, `substituteName`, `printName`, `requiredBufferLength`; methods: `readErrorContext`, `readErrorData`, `getErrorData`, `read`, `readOffsettedString`, `isAbsolute`, `getUnparsedPathLength`, `getSubstituteName`, `getPrintName`, `getRequiredBufferLength`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 56-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2FileId`; state fields: `persistentHandle`, `volatileHandle`; methods: `write`, `read`, `toString`; notable imports: `com.hierynomus.protocol.commons.ByteArrayUtils`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.ByteArrayUtils`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Functions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Functions.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Functions.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 30-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Functions`; state fields: `EMPTY_BYTES`; methods: `unicode`; notable imports: `com.hierynomus.protocol.commons.Charsets`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.Charsets`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; UTF-16LE byte counts must remain even and must be counted as bytes on the wire, not Java characters.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Functions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2GlobalCapability.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2GlobalCapability.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2GlobalCapability.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 41-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2GlobalCapability implements EnumWithValue<SMB2GlobalCapability>`; wire values: `SMB2_GLOBAL_CAP_DFS`, `SMB2_GLOBAL_CAP_LEASING`, `SMB2_GLOBAL_CAP_LARGE_MTU`, `SMB2_GLOBAL_CAP_MULTI_CHANNEL`, `SMB2_GLOBAL_CAP_PERSISTENT_HANDLES`, `SMB2_GLOBAL_CAP_DIRECTORY_LEASING`, `SMB2_GLOBAL_CAP_ENCRYPTION`; state fields: `i`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2GlobalCapability.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ImpersonationLevel.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ImpersonationLevel.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ImpersonationLevel.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 39-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ImpersonationLevel implements EnumWithValue<SMB2ImpersonationLevel>`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ImpersonationLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2LockFlag.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2LockFlag.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2LockFlag.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 39-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2LockFlag implements EnumWithValue<SMB2LockFlag>`; wire values: `SMB2_LOCKFLAG_SHARED_LOCK`, `SMB2_LOCKFLAG_EXCLUSIVE_LOCK`, `SMB2_LOCKFLAG_UNLOCK`, `SMB2_LOCKFLAG_FAIL_IMMEDIATELY`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2LockFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 65-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2MessageCommandCode`; wire values: `SMB2_NEGOTIATE`, `SMB2_SESSION_SETUP`, `SMB2_LOGOFF`, `SMB2_TREE_CONNECT`, `SMB2_TREE_DISCONNECT`, `SMB2_CREATE`, `SMB2_CLOSE`, `SMB2_FLUSH`, `SMB2_READ`, `SMB2_WRITE`, `SMB2_LOCK`, `SMB2_IOCTL`, `SMB2_CANCEL`, `SMB2_ECHO`; state fields: `cache`, `value`; methods: `getValue`, `lookup`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java` converts parsed `SMB2PacketData` into concrete SMB2 response packet classes and decides which non-success NTSTATUS values still carry usable response bodies. The source was read as a complete 122-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2MessageConverter`; state fields: `logger`, `FSCTL_PIPE_PEEK`, `FSCTL_PIPE_TRANSCEIVE`, `FSCTL_DFS_GET_REFERRALS`, `FSCTL_SRV_COPYCHUNK`, `FSCTL_SRV_COPYCHUNK_WRITE`; methods: `getPacketInstance`, `readPacket`, `isSuccess`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.mssmb2.messages.*`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacket`, `com.hierynomus.smbj.common.SMBRuntimeException`, `org.slf4j.Logger`, `org.slf4j.LoggerFactory`.

## Control Flow

`readPacket` switches on the SMB2 command to instantiate the response class, then either calls `read` or `readError`. `isSuccess` treats selected warning/status codes as body-bearing success equivalents for session setup, change notify, read/query-info buffer overflow, and specific IOCTL controls.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.mssmb2.messages.*`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacket`, `com.hierynomus.smbj.common.SMBRuntimeException`, `org.slf4j.Logger`, `org.slf4j.LoggerFactory`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 38-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2MessageFlag implements EnumWithValue<SMB2MessageFlag>`; wire values: `SMB2_FLAGS_SERVER_TO_REDIR`, `SMB2_FLAGS_ASYNC_COMMAND`, `SMB2_FLAGS_RELATED_OPERATIONS`, `SMB2_FLAGS_SIGNED`, `SMB2_FLAGS_PRIORITY_MASK`, `SMB2_FLAGS_DFS_OPERATIONS`, `SMB2_FLAGS_REPLAY_OPERATION`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 35-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2MultiCreditPacket extends SMB2Packet`; state fields: `maxPayloadSize`; methods: `getMaxPayloadSize`, `getPayloadSize`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 164-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Packet extends SMBPacket<SMB2PacketData, SMB2PacketHeader>`; state fields: `SINGLE_CREDIT_PAYLOAD_SIZE`, `structureSize`, `error`; methods: `getSequenceNumber`, `getStructureSize`, `getBuffer`, `write`, `writeTo`, `read`, `readMessage`, `isSuccess`, `isIntermediateAsyncResponse`, `getMaxPayloadSize`, `getCreditsAssigned`, `setCreditsAssigned`, `getError`, `setError`, `getPacket`, `toString`; notable imports: `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`.

## Control Flow

`write` writes the header followed by subclass body and records message end. `read` binds packet data/header, delegates body parsing to `readMessage`, then jumps to the message end. `readError` follows the same buffer discipline using `SMB2Error`.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 94-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketData extends SMBPacketData<SMB2PacketHeader>`; methods: `getSequenceNumber`, `isSuccess`, `isIntermediateAsyncResponse`, `isOplockBreakNotification`, `isCompounded`, `next`, `isDecrypted`, `toString`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacketData`, `static com.hierynomus.mssmb2.SMB2MessageCommandCode.SMB2_OPLOCK_BREAK`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`.

## Control Flow

Construction reads an SMB2 header from the buffer. Helpers classify success, pending async responses, oplock break notifications, and compounded packets; `next` reuses the same buffer at the next compounded message.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacketData`, `static com.hierynomus.mssmb2.SMB2MessageCommandCode.SMB2_OPLOCK_BREAK`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 32-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketFactory implements PacketFactory<SMB2PacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 274-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketHeader implements SMBHeader`; state fields: `EMPTY_SIGNATURE`, `STRUCTURE_SIZE`, `SIGNATURE_OFFSET`, `SIGNATURE_SIZE`, `PROTOCOL_ID`, `dialect`, `creditCharge`, `creditRequest`, `creditResponse`, `message`, `messageId`, `asyncId`, `sessionId`, `treeId`, `statusCode`, `flags`; methods: `writeTo`, `writeChannelSequenceReserved`, `writeCreditRequest`, `writeCreditCharge`, `setMessageId`, `setMessageType`, `getMessage`, `getTreeId`, `setTreeId`, `getSessionId`, `setSessionId`, `setDialect`, `isFlagSet`, `setFlag`, `getMessageId`, `setCreditRequest`, `getCreditRequest`, `getCreditResponse`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `java.util.Arrays`.

## Control Flow

`writeTo` writes the 64-byte SMB2 header and chooses async-id versus tree-id layout from flags. `readFrom` validates the protocol id, captures status, command, credits, flags, ids, signature, and derives message end from compounding offset or packet size.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `java.util.Arrays`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareAccess.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareAccess.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareAccess.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 43-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ShareAccess implements EnumWithValue<SMB2ShareAccess>`; wire values: `FILE_SHARE_READ`, `FILE_SHARE_WRITE`, `FILE_SHARE_DELETE`; state fields: `ALL`, `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`, `java.util.Collections`, `java.util.EnumSet`, `java.util.Set`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`, `java.util.Collections`, `java.util.EnumSet`, `java.util.Set`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareAccess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareCapabilities.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareCapabilities.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareCapabilities.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 40-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ShareCapabilities implements EnumWithValue<SMB2ShareCapabilities>`; wire values: `SMB2_SHARE_CAP_DFS`, `SMB2_SHARE_CAP_CONTINUOUS_AVAILABILITY`, `SMB2_SHARE_CAP_SCALEOUT`, `SMB2_SHARE_CAP_CLUSTER`, `SMB2_SHARE_CAP_ASYMMETRIC`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 50-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ShareFlags implements EnumWithValue<SMB2ShareFlags>`; wire values: `SMB2_SHAREFLAG_MANUAL_CACHING`, `SMB2_SHAREFLAG_AUTO_CACHING`, `SMB2_SHAREFLAG_VDO_CACHING`, `SMB2_SHAREFLAG_NO_CACHING`, `SMB2_SHAREFLAG_DFS`, `SMB2_SHAREFLAG_DFS_ROOT`, `SMB2_SHAREFLAG_RESTRICT_EXCLUSIVE_OPENS`, `SMB2_SHAREFLAG_FORCE_SHARED_DELETE`, `SMB2_SHAREFLAG_ALLOW_NAMESPACE_CACHING`, `SMB2_SHAREFLAG_ACCESS_BASED_DIRECTORY_ENUM`, `SMB2_SHAREFLAG_FORCE_LEVELII_OPLOCK`, `SMB2_SHAREFLAG_ENABLE_HASH_V1`, `SMB2_SHAREFLAG_ENABLE_HASH_V2`, `SMB2_SHAREFLAG_ENCRYPT_DATA`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 119-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TransformHeader implements SMBHeader`; state fields: `ENCRYPTED_PROTOCOL_ID`, `headerStartPosition`, `signature`, `nonce`, `originalMessageSize`, `flagsEncryptionAlgorithm`, `sessionId`, `messageEndPosition`; methods: `writeTo`, `readFrom`, `getHeaderStartPosition`, `getMessageEndPosition`, `setMessageEndPosition`, `getSignature`, `setSignature`, `getNonce`, `getOriginalMessageSize`, `getFlagsEncryptionAlgorithm`, `getSessionId`, `isEncrypted`; notable imports: `java.util.Arrays`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`.

## Control Flow

`writeTo` emits the transform header; `readFrom` validates the transform protocol id, records start/end positions, and parses the algorithm/session/nonce or compression fields needed by encryption or decompression layers.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `java.util.Arrays`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketData.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 36-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB3CompressedPacketData extends SMBPacketData<SMB2CompressionTransformHeader>`; state fields: `decrypted`; methods: `isDecrypted`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketFactory.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 33-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB3CompressedPacketFactory implements PacketFactory<SMB3CompressedPacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`.

## Control Flow

`read` wraps raw transport bytes in the corresponding transform packet-data object, while `canHandle` checks the transform protocol id before dispatch.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressedPacketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressionAlgorithm.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressionAlgorithm.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressionAlgorithm.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 36-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB3CompressionAlgorithm implements EnumWithValue<SMB3CompressionAlgorithm>`; wire values: `NONE`, `LZNT1`, `LZ77`, `LZ77_HUFFMAN`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3CompressionAlgorithm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketData.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 35-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB3EncryptedPacketData extends SMBPacketData<SMB2TransformHeader>`; methods: `getCipherText`, `toString`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacketData`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 33-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB3EncryptedPacketFactory implements PacketFactory<SMB3EncryptedPacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`.

## Control Flow

`read` wraps raw transport bytes in the corresponding transform packet-data object, while `canHandle` checks the transform protocol id before dispatch.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptionCipher.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptionCipher.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptionCipher.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 48-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB3EncryptionCipher implements EnumWithValue<SMB3EncryptionCipher>`; wire values: `AES_128_CCM`, `AES_128_GCM`; state fields: `value`, `algorithmName`, `nonceLength`; methods: `getValue`, `getAlgorithmName`, `getNonceLength`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptionCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3HashAlgorithm.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3HashAlgorithm.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3HashAlgorithm.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 44-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB3HashAlgorithm implements EnumWithValue<SMB3HashAlgorithm>`; wire values: `SHA_512`; state fields: `value`, `algorithmName`; methods: `getValue`, `getAlgorithmName`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3HashAlgorithm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java` wraps SMB protocol failures with the failed command and NTSTATUS code so higher SMBJ APIs can expose protocol errors consistently. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMBApiException extends SMBRuntimeException`; state fields: `failedCommand`, `statusCode`; methods: `getStatus`, `getStatusCode`, `getFailedCommand`, `getMessage`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.smbj.common.SMBRuntimeException`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.smbj.common.SMBRuntimeException`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java` models FSCTL server-side copy-chunk request or response data used by SMB2 IOCTL copy offload. The source was read as a complete 87-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class CopyChunkRequest`; state fields: `ctlCode`, `resumeKey`, `chunks`, `srcOffset`, `tgtOffset`, `length`; methods: `getCtlCode`, `getResumeKey`, `getChunks`, `write`, `getSrcOffset`, `getTgtOffset`, `getLength`; notable imports: `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

The request writer emits the resume key and one or more chunk descriptors; the response parser reads the three count fields returned by the server after copy offload.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It is passed through SMB2 IOCTL requests for `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java` models FSCTL server-side copy-chunk request or response data used by SMB2 IOCTL copy offload. The source was read as a complete 55-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class CopyChunkResponse`; state fields: `chunksWritten`, `chunkBytesWritten`, `totalBytesWritten`; methods: `getChunksWritten`, `getChunkBytesWritten`, `getTotalBytesWritten`, `read`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

The request writer emits the resume key and one or more chunk descriptors; the response parser reads the three count fields returned by the server after copy offload.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It is passed through SMB2 IOCTL requests for `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Cancel.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Cancel.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Cancel.java` serializes or parses the `SMB2 Cancel` command body for SMB2 request/response processing. The source was read as a complete 53-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Cancel extends SMB2Packet`; methods: `writeTo`, `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2MessageFlag`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2MessageFlag`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Cancel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java` serializes or parses the `SMB2 ChangeNotifyRequest` command body for SMB2 request/response processing. The source was read as a complete 57-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2ChangeNotifyRequest extends SMB2MultiCreditPacket`; state fields: `fileId`, `completionFilter`, `flags`; methods: `writeTo`; notable imports: `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponse.java` serializes or parses the `SMB2 ChangeNotifyResponse` command body for SMB2 request/response processing. The source was read as a complete 72-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2ChangeNotifyResponse extends SMB2Packet`; methods: `readMessage`, `readFileNotifyInfo`, `getFileNotifyInfoList`; notable imports: `java.util.ArrayList`, `java.util.List`, `com.hierynomus.msfscc.directory.FileNotifyInformation`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `java.util.ArrayList`, `java.util.List`, `com.hierynomus.msfscc.directory.FileNotifyInformation`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java` serializes or parses the `SMB2 Close` command body for SMB2 request/response processing. The source was read as a complete 103-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Close extends SMB2Packet`; state fields: `fileId`, `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `allocationSize`, `size`, `fileAttributes`; methods: `writeTo`, `readMessage`, `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getAllocationSize`, `getSize`, `getFileAttributes`, `setFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java` serializes or parses the `SMB2 CreateRequest` command body for SMB2 request/response processing. The source was read as a complete 102-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CreateRequest extends SMB2Packet`; state fields: `fileAttributes`, `shareAccess`, `createDisposition`, `createOptions`, `path`, `accessMask`, `impersonationLevel`; methods: `writeTo`, `getCreateDisposition`; notable imports: `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.ensureNotNull`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.ensureNotNull`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateResponse.java` serializes or parses the `SMB2 CreateResponse` command body for SMB2 request/response processing. The source was read as a complete 101-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CreateResponse extends SMB2Packet`; state fields: `createAction`, `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `fileAttributes`, `fileId`; methods: `readMessage`, `getCreateAction`, `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getFileAttributes`, `getFileId`, `setFileAttributes`, `setFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.SMB2CreateAction`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.SMB2CreateAction`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Echo.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Echo.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Echo.java` serializes or parses the `SMB2 Echo` command body for SMB2 request/response processing. The source was read as a complete 47-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Echo extends SMB2Packet`; methods: `writeTo`, `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Echo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Flush.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Flush.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Flush.java` serializes or parses the `SMB2 Flush` command body for SMB2 request/response processing. The source was read as a complete 53-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Flush extends SMB2Packet`; state fields: `fileId`; methods: `writeTo`, `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Flush.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlRequest.java` serializes or parses the `SMB2 IoctlRequest` command body for SMB2 request/response processing. The source was read as a complete 76-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2IoctlRequest extends SMB2MultiCreditPacket`; state fields: `controlCode`, `fileId`, `inputData`, `fsctl`, `maxOutputResponse`; methods: `writeTo`, `getControlCode`; notable imports: `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.io.ByteChunkProvider`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.io.ByteChunkProvider`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlResponse.java` serializes or parses the `SMB2 IoctlResponse` command body for SMB2 request/response processing. The source was read as a complete 77-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2IoctlResponse extends SMB2Packet`; state fields: `controlCode`, `fileId`; methods: `readMessage`, `getOutputBuffer`, `getInputBuffer`, `getControlCode`, `getFileId`; notable imports: `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2IoctlResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockRequest.java` serializes or parses the `SMB2 LockRequest` command body for SMB2 request/response processing. The source was read as a complete 74-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2LockRequest extends SMB2Packet`; state fields: `lockSequenceNumber`, `lockSequenceIndex`, `fileId`, `lockElements`; methods: `writeTo`, `getLsnAndLsi`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.messages.submodule.SMB2LockElement`, `com.hierynomus.smb.SMBBuffer`, `java.util.List`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.messages.submodule.SMB2LockElement`, `com.hierynomus.smb.SMBBuffer`, `java.util.List`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java` serializes or parses the `SMB2 LockResponse` command body for SMB2 request/response processing. The source was read as a complete 31-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2LockResponse extends SMB2Packet`; methods: `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Logoff.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Logoff.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Logoff.java` serializes or parses the `SMB2 Logoff` command body for SMB2 request/response processing. The source was read as a complete 48-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Logoff extends SMB2Packet`; methods: `writeTo`, `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Logoff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateRequest.java` serializes or parses the `SMB2 NegotiateRequest` command body for SMB2 request/response processing. The source was read as a complete 144-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2NegotiateRequest extends SMB2Packet`; state fields: `dialects`, `clientGuid`, `clientSigningRequired`, `capabilities`, `negotiateContextList`; methods: `buildNegotiateContextList`, `writeTo`, `securityMode`, `putNegotiateContextList`, `putDialects`, `putNegotiateContextOrStartTime`, `putCapabilities`, `getNegotiateContextList`; notable imports: `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.mssmb2.messages.negotiate.SMB2EncryptionCapabilities`, `com.hierynomus.mssmb2.messages.negotiate.SMB2NegotiateContext`, `com.hierynomus.mssmb2.messages.negotiate.SMB2PreauthIntegrityCapabilities`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.*`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.mssmb2.messages.negotiate.SMB2EncryptionCapabilities`, `com.hierynomus.mssmb2.messages.negotiate.SMB2NegotiateContext`, `com.hierynomus.mssmb2.messages.negotiate.SMB2PreauthIntegrityCapabilities`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.*`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateResponse.java` serializes or parses the `SMB2 NegotiateResponse` command body for SMB2 request/response processing. The source was read as a complete 171-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2NegotiateResponse extends SMB2Packet`; state fields: `securityMode`, `dialect`, `serverGuid`, `capabilities`, `maxTransactSize`, `maxReadSize`, `maxWriteSize`, `systemTime`, `serverStartTime`, `gssToken`, `negotiateContextList`; methods: `readMessage`, `readNegotiateContextList`, `readSecurityBuffer`, `readNegotiateContextOffset`, `readNegotiateContextCount`, `getGssToken`, `getSecurityMode`, `getDialect`, `getServerGuid`, `getCapabilities`, `getMaxTransactSize`, `getMaxReadSize`, `getMaxWriteSize`, `getSystemTime`, `getServerStartTime`, `getNegotiateContextList`, `setDialect`, `setSystemTime`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.messages.negotiate.SMB2NegotiateContext`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.messages.negotiate.SMB2NegotiateContext`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2NegotiateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryRequest.java` serializes or parses the `SMB2 QueryDirectoryRequest` command body for SMB2 request/response processing. The source was read as a complete 86-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2QueryDirectoryRequest extends SMB2MultiCreditPacket`; state fields: `fileInformationClass`, `flags`, `fileIndex`, `fileId`, `searchPattern`, `value`; methods: `writeTo`, `getValue`; notable imports: `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponse.java` serializes or parses the `SMB2 QueryDirectoryResponse` command body for SMB2 request/response processing. The source was read as a complete 44-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2QueryDirectoryResponse extends SMB2Packet`; state fields: `outputBuffer`; methods: `readMessage`, `getOutputBuffer`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoRequest.java` serializes or parses the `SMB2 QueryInfoRequest` command body for SMB2 request/response processing. The source was read as a complete 138-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2QueryInfoRequest extends SMB2Packet`; state fields: `MAX_OUTPUT_BUFFER_LENGTH`, `fileId`, `infoType`, `fileInformationClass`, `fileSystemInformationClass`, `inputBuffer`, `securityInformation`, `value`; methods: `writeTo`, `getValue`; notable imports: `com.hierynomus.msdtyp.SecurityInformation`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.msfscc.FileSystemInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.SecurityInformation`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.msfscc.FileSystemInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoResponse.java` serializes or parses the `SMB2 QueryInfoResponse` command body for SMB2 request/response processing. The source was read as a complete 43-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2QueryInfoResponse extends SMB2Packet`; methods: `readMessage`, `getOutputBuffer`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2QueryInfoResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadRequest.java` serializes or parses the `SMB2 ReadRequest` command body for SMB2 request/response processing. The source was read as a complete 56-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2ReadRequest extends SMB2MultiCreditPacket`; state fields: `offset`, `fileId`; methods: `writeTo`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2MultiCreditPacket`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2MultiCreditPacket`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadResponse.java` serializes or parses the `SMB2 ReadResponse` command body for SMB2 request/response processing. The source was read as a complete 49-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2ReadResponse extends SMB2Packet`; state fields: `dataLength`, `data`; methods: `readMessage`, `getDataLength`, `getData`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ReadResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java` serializes or parses the `SMB2 SessionSetup` command body for SMB2 request/response processing. The source was read as a complete 149-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2SessionSetup extends SMB2Packet`; state fields: `negotiatedDialect`, `securityMode`, `clientCapabilities`, `securityBuffer`, `previousSessionId`, `sessionFlags`, `value`; methods: `writeTo`, `readMessage`, `readSecurityBuffer`, `putFlags`, `getSessionFlags`, `setSessionFlags`, `setPreviousSessionId`, `setSecurityBuffer`, `getSecurityBuffer`, `getValue`; notable imports: `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`, `java.util.Set`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`, `java.util.Set`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.protocol.commons.EnumWithValue`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoRequest.java` serializes or parses the `SMB2 SetInfoRequest` command body for SMB2 request/response processing. The source was read as a complete 85-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2SetInfoRequest extends SMB2Packet`; state fields: `fileId`, `infoType`, `fileInfoClass`, `buffer`, `securityInformation`, `value`; methods: `writeTo`, `getValue`; notable imports: `com.hierynomus.msdtyp.SecurityInformation`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.SecurityInformation`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoResponse.java` serializes or parses the `SMB2 SetInfoResponse` command body for SMB2 request/response processing. The source was read as a complete 31-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2SetInfoResponse extends SMB2Packet`; methods: `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SetInfoResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectRequest.java` serializes or parses the `SMB2 TreeConnectRequest` command body for SMB2 request/response processing. The source was read as a complete 75-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TreeConnectRequest extends SMB2Packet`; state fields: `dialect`, `isClusterReconnect`, `smbPath`; methods: `writeTo`, `putFlags`, `getSmbPath`, `setSmbPath`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java` serializes or parses the `SMB2 TreeConnectResponse` command body for SMB2 request/response processing. The source was read as a complete 101-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TreeConnectResponse extends SMB2Packet`; state fields: `shareType`, `shareFlags`, `capabilities`, `maximalAccess`; methods: `readMessage`, `setShareType`, `isDiskShare`, `isNamedPipe`, `isPrinterShare`, `getShareFlags`, `setShareFlags`, `getCapabilities`, `setCapabilities`, `getMaximalAccess`; notable imports: `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2ShareCapabilities`, `com.hierynomus.mssmb2.SMB2ShareFlags`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2ShareCapabilities`, `com.hierynomus.mssmb2.SMB2ShareFlags`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeDisconnect.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeDisconnect.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeDisconnect.java` serializes or parses the `SMB2 TreeDisconnect` command body for SMB2 request/response processing. The source was read as a complete 48-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TreeDisconnect extends SMB2Packet`; methods: `writeTo`, `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeDisconnect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteRequest.java` serializes or parses the `SMB2 WriteRequest` command body for SMB2 request/response processing. The source was read as a complete 53-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2WriteRequest extends SMB2MultiCreditPacket`; state fields: `fileId`, `byteProvider`; methods: `writeTo`; notable imports: `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.io.ByteChunkProvider`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.io.ByteChunkProvider`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteResponse.java` serializes or parses the `SMB2 WriteResponse` command body for SMB2 request/response processing. The source was read as a complete 42-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2WriteResponse extends SMB2Packet`; state fields: `bytesWritten`; methods: `readMessage`, `getBytesWritten`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2WriteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java` models an SMB 3.1.1 negotiate context advertising compression algorithms during dialect negotiation. The source was read as a complete 75-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CompressionCapabilities extends SMB2NegotiateContext`; state fields: `compressionAlgorithms`; methods: `writeContext`, `readContext`, `getCompressionAlgorithms`; notable imports: `com.hierynomus.mssmb2.SMB3CompressionAlgorithm`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB3CompressionAlgorithm`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java -->
