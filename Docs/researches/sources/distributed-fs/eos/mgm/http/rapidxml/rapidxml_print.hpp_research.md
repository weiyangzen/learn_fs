# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_print.hpp

## Purpose
`rapidxml_print.hpp` implements RapidXML DOM serialization. It prints XML nodes to output iterators or streams, escaping data and attributes and optionally suppressing indentation.

## Important APIs, Types, and Functions
The public API is `print(out, node, flags)`, stream `print(out, node, flags)`, `operator<<`, and `print_no_indenting`. Internal helpers include `print_node()`, `print_children()`, `print_attributes()`, and node-type-specific printers for data, CDATA, element, declaration, comment, doctype, and processing-instruction nodes. Character helpers copy, escape, fill indentation, and choose attribute quote style.

## Control Flow
`print()` dispatches by node type. Document nodes print children. Element nodes print an opening tag and attributes, then either self-close, print inline data, or recursively print children with increased indentation before writing the closing tag. Attribute values are escaped and quoted with the quote character that minimizes expansion. Data nodes escape XML-sensitive characters, while CDATA, comments, doctype, and PI values are emitted mostly verbatim.

## State and Persistence Behavior
The printer is stateless and does not mutate the DOM. Output is streamed through the caller's iterator or stream. Formatting state is limited to flags and the current indentation depth.

## Dependencies and Integration Points
It depends on `rapidxml.hpp` and optionally `<ostream>`/`<iterator>` unless `RAPIDXML_NO_STREAMS` is defined. It is the serialization companion for XML DOMs built by the embedded RapidXML parser.

## Risks
CDATA, comments, PI, and doctype values are not validated or escaped, so invalid sequences already present in the DOM can produce invalid XML. Indenting uses tabs and appends a newline after every printed node unless disabled. Attribute printing skips attributes with null name or value pointers. Output iterators must be valid and capable of receiving all emitted characters.

## Test Signals
Tests should cover escaping for text and attributes, quote selection, self-closing elements, inline data versus child-node formatting, `print_no_indenting`, stream operator output, declaration/comment/doctype/PI serialization, and invalid DOM content behavior.
