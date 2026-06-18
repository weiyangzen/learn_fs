# sources/control-plane/longhorn/scripts/update-uninstall-manifest.py

## Purpose
Python utility that synchronizes the Longhorn API resources in `uninstall/uninstall.yaml` ClusterRole from CRDs present in `deploy/longhorn.yaml`.

## Important APIs, Classes, and Functions
Class `YAMLResourceProcessor` stores `longhorn_manifest`, `uninstall_file`, and temp output path. `load_yaml_documents` streams non-empty YAML docs with PyYAML and wraps parse/IO failures. `extract_crd_resources` scans for `CustomResourceDefinition` documents and appends the first DNS segment of each CRD name, removing the `.longhorn.io` suffix by split. `update_cluster_role` replaces the `resources` list for rules whose `apiGroups` equals `["longhorn.io"]`. `process_files` writes all updated docs to `uninstall.tmp.yaml`. `main` runs with fixed repo-relative paths and atomically replaces the uninstall file with `os.replace`.

## Control Flow
The script reads generated deploy manifest CRDs, builds the resource list, streams the existing uninstall manifest, updates matching ClusterRole rules, dumps each document followed by `---`, replaces the original file, and reports success. Exceptions print an error and exit non-zero.

## State and Persistence
Mutates `uninstall/uninstall.yaml` in place via a temp file. It reads only local YAML manifests and does not touch a cluster.

## Dependencies and Integration Points
Requires Python, PyYAML, and execution from the Longhorn repo root because paths are relative. Integrates with manifest generation so the uninstall job's RBAC tracks current Longhorn CRDs.

## Risks
The CRD resource derivation uses `name.split(".")[0]`, which works for standard `<plural>.longhorn.io` names but would truncate any plural containing dots. `yaml.dump` may reorder formatting, comments, and style. It updates every ClusterRole document with a longhorn.io rule, not just a named role. No explicit test verifies that generated resources match Kubernetes plural resource names.

## Test Signals
Run after `generate-longhorn-yaml.sh`, diff `uninstall/uninstall.yaml`, and parse with Kubernetes tooling. Compare extracted CRD plural names to the ClusterRole longhorn.io resource list.
