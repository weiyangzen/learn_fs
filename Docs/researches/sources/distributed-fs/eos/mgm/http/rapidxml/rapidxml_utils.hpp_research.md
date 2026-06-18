# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_utils.hpp

## Purpose
`rapidxml_utils.hpp` provides small convenience utilities around RapidXML: loading an entire file/stream into a null-terminated buffer and counting a node's children or attributes.

## Important APIs, Types, and Functions
`rapidxml::file<Ch>` owns a `std::vector<Ch>` buffer and has constructors for filenames and input streams. `data()` returns mutable or const buffer pointers, and `size()` returns the vector size including the trailing zero. `count_children(node)` and `count_attributes(node)` iterate sibling/attribute lists and return counts.

## Control Flow
The filename constructor opens a binary stream, determines size with seek/tell, resizes the vector to `size + 1`, reads the content, and appends a zero. The stream constructor reads via iterators, checks stream state, and appends a zero. Counting helpers walk `first_node()/next_sibling()` or `first_attribute()/next_attribute()`.

## State and Persistence Behavior
`file<Ch>` owns the buffer for its lifetime, which is important because RapidXML DOM nodes usually point into the parsed source buffer. The helpers do not persist anything outside memory.

## Dependencies and Integration Points
The header depends on `rapidxml.hpp`, `vector`, `string`, `fstream`, and `stdexcept`. It is useful for callers that need a mutable, null-terminated buffer before passing data to `xml_document::parse()`.

## Risks
`size()` includes the trailing null, which can surprise callers expecting file byte count. The filename constructor uses `tellg()` cast to `size_t`, so stream errors or huge files need care. Loading is all-at-once and unsuitable for unbounded XML inputs. Counting helpers assume a valid node pointer.

## Test Signals
Tests should cover successful file and stream loading, missing-file exceptions, stream read failures, null termination, mutable `data()` compatibility with parsing, count helpers on empty and populated nodes, and expected `size()` semantics.
