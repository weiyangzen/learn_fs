# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_yaml_file.py

Purpose: Serializes kernel-doc parser/output results into YAML test files for unit/regression tests, supporting expected `man`, `rst`, and optional raw `KdocItem` representations.

Important APIs/types/functions: `KDocTestFile.__init__()` prepares the target YAML file, validates output directory existence, imports `yaml`, and creates selected `ManFormat`/`RestFormat` renderers from `yaml_content`. `set_filter()` forwards output filters to renderers. `get_kdoc_item()` converts an object to a dict and normalizes declaration, parameter, and section start lines relative to a requested start line. `output_symbols()` converts parsed symbols into named test entries. `write()` emits YAML with block-style multiline strings.

Control flow: The caller constructs the object with config and YAML options, sets filters, calls `output_symbols()` per source file, then `write()`. For each symbol, a unique lowercase test name is derived from the symbol or file name; selected output formats are rendered via `output_symbols(fname, [arg])`, and expected data is appended to `self.tests`.

State and persistence: `self.tests` accumulates YAML test cases; `self.test_names` prevents duplicate case names. `write()` persists `{"tests": self.tests}` to `self.test_file`.

Dependencies/integration: Depends on PyYAML, `kdoc.kdoc_output.ManFormat`, and `RestFormat`. It expects symbol objects to expose `name`, `declaration_start_line`, `get("source")`, and `vars()`-compatible fields.

Risks: `__init__()` calls `sys.exit()` but does not import `sys`, so missing PyYAML or missing output directory triggers `NameError` rather than the intended exit. `get_kdoc_item()` mutates the object dictionary returned by `vars(arg)`, including nested line-number maps. `start_line` is initialized in `output_symbols()` but not advanced per symbol, so relative line normalization is fixed at 1. Reusing `expected_dict` inside the loop requires careful reset to avoid bleeding fields between symbols.

Test signals: Cover missing PyYAML/output directory behavior, duplicate symbol names, `KdocItem` line normalization, source removal from `other_stuff`, and YAML block style for multiline rendered output.
