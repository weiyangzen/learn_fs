<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java

## Purpose
`XmlImageVisitor` is the legacy visitor-based XML writer for offline image viewing. It emits simple XML tags as the older `ImageVisitor` traversal calls arrive.

## APIs and Types
Constructors accept output filename and optional screen mirroring. It overrides `start`, `finish`, `finishAbnormally`, `visit`, `visitEnclosingElement`, and `leaveEnclosingElement`. A `Deque<ImageElement>` tracks open enclosing tags.

## Control Flow
`start` writes the XML declaration. Scalar `visit` emits a full tag through `writeTag`. Enclosing visits write an opening tag and push the element; the keyed overload emits one XML attribute without value mangling. `leaveEnclosingElement` pops and writes the closing tag, failing if there is no open element. Abnormal finish writes an XML comment before closing.

## State and Persistence
The tag stack is in memory. File output and close behavior come from `TextWriterImageVisitor`. Values are mangled through `XMLUtils.mangleXmlString`; attribute values are not passed through `XMLUtils`.

## Dependencies and Integration
It depends on the legacy `ImageVisitor` protocol, `ImageElement`, `TextWriterImageVisitor`, and `XMLUtils`. It is separate from protobuf-specific `PBImageXmlWriter`.

## Risks
Attribute values can produce invalid XML if they contain special characters. Unbalanced visitor calls fail at close-tag time or leave malformed output. Partial XML is expected on abnormal finish. It does not write a root element by itself; traversal must supply one.

## Test Signals
Tests should cover balanced and unbalanced nesting, special-character value mangling, keyed enclosing element attributes with special characters, abnormal finish output, and write/close propagation from the superclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java -->
