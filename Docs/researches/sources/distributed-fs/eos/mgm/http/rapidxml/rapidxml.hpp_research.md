# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml.hpp

## Purpose
`rapidxml.hpp` is the embedded RapidXML 1.13 header providing a non-validating XML parser and DOM implementation. It is designed for speed, in-place parsing, and pool-backed DOM allocation.

## Important APIs, Types, and Functions
The public surface includes `parse_error`, parse flags such as `parse_non_destructive`, `parse_fastest`, and `parse_full`, `node_type`, `memory_pool<Ch>`, `xml_base<Ch>`, `xml_attribute<Ch>`, `xml_node<Ch>`, and `xml_document<Ch>`. `memory_pool` allocates nodes, attributes, and strings from a static block plus dynamic blocks. `xml_node` exposes tree/attribute traversal and mutation methods. `xml_document::parse<Flags>()` is the main parser entry and `clear()` resets the DOM and pool.

## Control Flow
Parsing starts with BOM skipping, then repeatedly scans top-level nodes. `parse_node()` dispatches elements, declarations, processing instructions, comments, CDATA, and doctype. Element parsing extracts the name, attributes, and contents. Text and attribute values are scanned through lookup-table predicates, optionally translating XML entities, normalizing whitespace, trimming text, and inserting string terminators into the source buffer. Closing tag validation is optional.

## State and Persistence Behavior
DOM nodes do not own external strings unless those strings were allocated from the document pool. By default parsing mutates the input buffer by inserting null terminators and replacing entity references. `parse_non_destructive` prevents those mutations at the cost of requiring `name_size()` and `value_size()` aware consumers. All pool allocations are freed together by `clear()` or destruction; individual free is not supported.

## Dependencies and Integration Points
The header is self-contained apart from standard library headers unless `RAPIDXML_NO_STDLIB` or `RAPIDXML_NO_EXCEPTIONS` are defined. In this EOS tree it supports XML parsing used by MGM HTTP/WebDAV code and is paired with `rapidxml_print.hpp` and `rapidxml_utils.hpp`.

## Risks
The parser is non-validating and accepts some constructs leniently, including multiple doctypes unless flags dictate otherwise. Input buffers must outlive the DOM and must be mutable unless non-destructive parsing is selected. Many accessors rely on assertions for misuse such as requesting last child when none exists. There is no built-in XXE expansion, but doctype text can be retained if requested. Deep or hostile XML can consume pool memory or recursion-like call depth through nested parsing.

## Test Signals
Tests should cover destructive versus non-destructive parsing, entity translation, UTF-8 numeric entities, whitespace trim/normalize combinations, closing-tag validation, comments/declarations/PI/doctype flags, CDATA handling, DOM mutation methods, memory-pool custom allocators, clear/reparse lifecycle, and malformed XML exceptions with useful `where()` pointers.
