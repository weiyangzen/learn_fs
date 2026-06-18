# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemUtil.java

`ViewFileSystemUtil` is a public utility class for identifying viewfs instances and collecting filesystem status per matching mount point. It is stateless and non-instantiable.

Important APIs are `isViewFileSystem(FileSystem)`, `isViewFileSystemOverloadScheme(FileSystem)`, and `getStatus(FileSystem, Path)`. The first checks for the literal `viewfs` scheme; the second checks `instanceof ViewFileSystemOverloadScheme`. `getStatus` validates that the input filesystem is either a viewfs or overload-scheme instance, casts to `ViewFileSystem`, obtains the viewfs URI path, iterates public mount points, compares path components, and returns a map of matching mount points to `FsStatus`.

Control flow distinguishes three cases: the path is over a specific mount point, the path is an internal directory leading to one or more mount points, or the path is `/` and includes all mount points. If none apply, it throws `NotInMountpointException`. For matches, it calls `viewFileSystem.getStatus(path)` and stores the result by `MountPoint`.

Dependencies are `FileSystem`, `FsConstants`, `FsStatus`, `Path`, `UnsupportedFileSystemException`, `ViewFileSystem.MountPoint`, and `InodeTree.breakIntoPathComponents`.

Risks include scheme-based detection missing overload schemes unless callers use the second helper, map overwrites if mount point equality changes, path-component edge cases at root, and `getStatus(path)` behavior for fallback/internal dirs. Tests should cover non-viewfs rejection, root status over all mounts, internal directory status aggregation, path over a single mount, unrelated paths throwing `NotInMountpointException`, and overload-scheme inputs.
