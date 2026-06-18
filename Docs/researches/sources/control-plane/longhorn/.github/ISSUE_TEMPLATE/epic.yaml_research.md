## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/epic.yaml

### Purpose
`epic.yaml` defines the issue form for grouping features, enhancements, or tasks under an Epic.

### Important APIs, Types, And Functions
It sets title prefix `[EPIC]`, issue type `Epic`, label `Epic`, and asks for problem context, task breakdown, and optional additional context.

### Control Flow
GitHub renders required textareas for problem and tasks; submission creates an Epic issue with the configured metadata.

### State, Persistence, And Dependencies
The file persists issue intake schema and depends on GitHub issue type/label configuration.

### Integration Points
Epic issues can be linked manually to child issues and may be picked up by project automation through labels or type.

### Risks
The template asks users to create sub-task issues but does not automate that linkage. The `assignees` list has an empty item.

### Test Signals
Create-form rendering and resulting issue metadata are the main validation signals.
