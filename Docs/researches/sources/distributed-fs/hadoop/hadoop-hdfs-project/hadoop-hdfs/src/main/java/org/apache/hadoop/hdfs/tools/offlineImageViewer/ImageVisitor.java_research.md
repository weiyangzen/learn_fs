## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageVisitor.java

Purpose: `ImageVisitor` is the legacy visitor contract for fsimage traversal. Loaders emit structural `ImageElement` events, and concrete visitors transform those events into text, XML, statistics, or other views.

Important APIs and control flow: `ImageElement` enumerates all recognized fsimage fields and structural containers, including namespace metadata, inode fields, block fields, under-construction files, delegation tokens, snapshot metadata, and cache entries. Abstract lifecycle methods are `start`, `finish`, and `finishAbnormally`. Leaf values are delivered with `visit(ImageElement, String)` plus numeric convenience overloads. Containers are opened with `visitEnclosingElement`, optionally with a key/value attribute, and closed with `leaveEnclosingElement`.

State, persistence, and dependencies: the base class has no state or persistence. Implementations maintain traversal stacks and output writers.

Integration points: `ImageLoaderCurrent` drives this contract. Visitors in this subset include delimited, indented, ls, name distribution, and file distribution renderers; `XmlImageVisitor` and `TextWriterImageVisitor` are adjacent package dependencies.

Risks and test signals: contract correctness depends on balanced open/close events and consistent element meanings across layout versions. Tests should use small synthetic traversal sequences to validate each visitor, plus loader integration tests that assert expected event order for representative images. Adding new fsimage fields requires extending the enum and deciding how each visitor handles them.
