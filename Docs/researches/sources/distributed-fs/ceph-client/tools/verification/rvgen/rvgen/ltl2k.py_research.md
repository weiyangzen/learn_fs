<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py

## Purpose

Turns an LTL specification into generated kernel monitor C for rvgen. It subclasses `generator.Monitor`, calls `ltl2ba.create_graph()`, abbreviates atom names, and fills the LTL monitor template with state enums, atom enums, start-state logic, transition logic, and instrumentation placeholders.

## Important APIs, Types, and Functions

Source size: 277 lines, 8226 bytes. Functions/classes: line_len, break_long_line, build_condition_string, abbreviate_atoms, shorten, find_share_length, ltl2k, __init__, _fill_states, _fill_atoms, _fill_atoms_to_string, _fill_atom_values, _fill_transitions, _fill_start, fill_tracepoint_handlers_skel, fill_tracepoint_attach_probe, fill_tracepoint_detach_helper, fill_atoms_init, plus 5 more. Python imports: pathlib, ., ., .automata.

## Control Flow and Data Flow

Construction validates `MonitorType == per_task`, reads the spec file, builds the Buchi automaton, derives atom abbreviations, and chooses a model name. `_fill_start()` emits initial state selection, `_fill_transitions()` emits switch-based next-state calculation, `_fill_atom_values()` recursively emits boolean helper expressions, and `fill_main_c()` injects atom initialization skeleton code into the template.

## State and Persistence Behavior

Generated state is textual C derived from `self.atoms`, `self.atoms_abbr`, `self.ba`, and `self.ltl`. Runtime monitor state lives in kernel `struct ltl_monitor`; this Python module itself only persists generated source output through the rvgen generator framework.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Column breaking is heuristic and can split only on spaces. Atom abbreviation can collide for similarly named atoms. The tracepoint attach/detach skeleton contains TODO placeholders and the detach helper names `handle_sample_event`, which must be reconciled with generated handlers.

## Test Signals

Use golden-file generation for representative formulas, compile generated headers with `RV_MAX_BA_STATES` and `RV_MAX_LTL_ATOM` limits, check line-length handling, and verify generated transition predicates against the Buchi graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py -->
