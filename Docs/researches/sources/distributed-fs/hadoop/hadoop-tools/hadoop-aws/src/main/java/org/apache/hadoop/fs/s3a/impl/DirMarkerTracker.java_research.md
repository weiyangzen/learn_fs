<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java

## Purpose

`DirMarkerTracker` tracks directory markers encountered during sorted S3 listings and identifies which markers are leaf markers versus surplus parent markers.

## Important APIs, Types, and Functions

Important methods are `markerFound()`, `fileFound()`, `pathFound()`, `removeParentMarkers()`, getters for leaf/surplus maps and counters, plus nested immutable `Marker`.

## Control Flow

When a marker is found it is first recorded as a candidate leaf, then all parent markers of that path are removed as surplus. When a file is found, parent markers are similarly removed. A cached `lastDirChecked` avoids rescanning the same parent for many siblings.

## State and Persistence Behavior

State is in-memory maps of leaf and optionally surplus markers, the base path, last checked directory, and counters. Nothing is persisted.

## Dependencies and Integration Points

It depends on Hadoop `Path` and `S3ALocatedFileStatus`. Rename, listing, auditing, and directory-marker cleanup code can use it while traversing list results.

## Risks and Edge Cases

The logic assumes listing order is alphanumeric with parents before children. If callers feed unsorted paths, leaf/surplus classification can be wrong. Recording surplus markers can consume memory in huge trees.

## Test Signals

Test parent marker removal, leaf marker preservation, surplus recording enabled/disabled, repeated sibling scan optimization, root/null parent handling, counters, and version id exposure from marker status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java -->
